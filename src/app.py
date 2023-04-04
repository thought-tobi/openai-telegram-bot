import logging
import os

import openai
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, MessageHandler, Application, CommandHandler
from telegram.ext import filters as Filters

from handlers import handle_text_prompt, handle_help, handle_reply, handle_error, handle_tts, handle_voice
from audio_handlers import handle_voice_note, summarize_voice_note

# setup
load_dotenv()
TOKEN = os.environ.get("TELEGRAM_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

# configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename="log")


def init_app() -> Application:
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("help", handle_help))
    app.add_handler(CommandHandler("tts", handle_tts))
    app.add_handler(CommandHandler("voice", handle_voice))
    app.add_handler(MessageHandler(Filters.TEXT & Filters.REPLY, handle_reply))
    app.add_handler(MessageHandler(Filters.VOICE & Filters.FORWARDED, summarize_voice_note))
    app.add_handler(MessageHandler(Filters.TEXT, handle_text_prompt))
    app.add_handler(MessageHandler(Filters.VOICE, handle_voice_note))
    app.add_error_handler(handle_error)
    return app


if __name__ == '__main__':
    application = init_app()
    logging.info("Starting application")
    application.run_polling()
