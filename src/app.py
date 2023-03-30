import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, Application
from telegram.ext import filters as Filters
import logging
import openai

# setup
load_dotenv()
TOKEN = os.environ.get("TELEGRAM_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

# configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.debug(f"Hello command received from {update.effective_user.first_name}")
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.debug(f"Echoing message: {update.message.text}")
    # generate openai response from message
    # Note: you need to be using OpenAI Python v0.27.0 for the code below to work

    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": update.message.text}]
    )
    logging.debug(f"OpenAI response: {openai_response}")
    text = openai_response["choices"][0]["message"]["content"]
    await update.message.reply_text(text)


def init_app() -> Application:
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("hello", hello))
    # add echo messagehandler
    app.add_handler(MessageHandler(Filters.TEXT, prompt))
    return app


if __name__ == '__main__':
    application = init_app()
    logging.info("Starting application")
    application.run_polling()
