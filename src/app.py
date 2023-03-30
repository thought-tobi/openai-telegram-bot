import logging
import os

import openai
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, Application, TypeHandler
from telegram.ext import filters as Filters

from handlers import handle_text_prompt, handle_voice_note

# setup
load_dotenv()
TOKEN = os.environ.get("TELEGRAM_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

# configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def init_app() -> Application:
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(Filters.TEXT, handle_text_prompt))
    app.add_handler(MessageHandler(Filters.VOICE, handle_voice_note))
    return app


if __name__ == '__main__':
    application = init_app()
    logging.info("Starting application")
    application.run_polling()
