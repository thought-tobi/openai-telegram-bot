import os
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, Application
from telegram.ext import filters as Filters
import logging
import openai

from src.session import Session

# setup
load_dotenv()
TOKEN = os.environ.get("TELEGRAM_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

# configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
sessions = []


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.debug(f"Hello command received from {update.effective_user.first_name}")
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


def _get_user_session(user_id: int) -> Session | None:
    for session in sessions:
        if session.user_id == user_id:
            if session.expires_at > datetime.now(timezone.utc):
                return session
            # also manages session, should probably be in a separate function
            else:
                logging.info(f"Session for user {user_id} expired, removing it from the list")
                sessions.remove(session)
    return None


def _create_new_session(update: Update) -> Session:
    session = Session(user_id=update.effective_user.id,
                      created_at=update.message.date,
                      messages=[])
    sessions.append(session)
    return session


async def prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    logging.info(f"Received message: {update.message.text} from user {user_id}")
    session = _get_user_session(user_id)
    if session:
        logging.info(f"Found active session for user {user_id}")
    else:
        logging.info(f"Creating new session for user {user_id}")
        session = _create_new_session(update)
    session.messages.append({"role": "user", "content": update.message.text})

    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=session.messages
    )

    text = openai_response["choices"][0]["message"]["content"]
    session.messages.append({"role": "assistant", "content": text})
    logging.info(session)
    await update.message.reply_text(text)


def init_app() -> Application:
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(MessageHandler(Filters.TEXT, prompt))
    return app


if __name__ == '__main__':
    application = init_app()
    logging.info("Starting application")
    application.run_polling()
