import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, Application
from telegram.ext import filters as Filters
import openai
import logging

from session import get_user_session

# setup
load_dotenv()
TOKEN = os.environ.get("TELEGRAM_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

# configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.debug(f"Hello command received from {update.effective_user.first_name}")
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info(f"Received message: {update.message.text} from user {update.effective_user.id}")
    session = get_user_session(update)

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
