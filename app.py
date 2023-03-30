import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, Application
from telegram.ext import filters as Filters
import logging

# setup
load_dotenv()
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.debug(f"Hello command received from {update.effective_user.first_name}")
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.debug(f"Echoing message: {update.message.text}")
    await update.message.reply_text(update.message.text)


def init_app() -> Application:
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("hello", hello))
    # add echo messagehandler
    app.add_handler(MessageHandler(Filters.TEXT, echo))
    return app


if __name__ == '__main__':
    application = init_app()
    logging.info("Starting application")
    application.run_polling()
