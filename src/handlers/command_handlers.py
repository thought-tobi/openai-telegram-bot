import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.edit_message import EditMessage
from src.session.prompts import HELP_TEXT, PROMPT_HELP, TTS_ENABLED
from src.session.session import get_user_session
from src.handlers.text_handlers import handle_prompt
from src.tts.elevenlabs import VOICES as ELEVEN_LABS_VOICES


async def handle_text_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info(f"Received message: {update.message.text} from user {update.effective_user.id}")
    await handle_prompt(update, update.message.text)


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text(HELP_TEXT)
    await handle_prompt(update, PROMPT_HELP, EditMessage(msg, "..."))


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    voice = update.message.text.replace("/voice ", "").lower()
    logging.info(voice)
    if voice in ELEVEN_LABS_VOICES:
        session = get_user_session(update.effective_user.id)
        session.set_voice(voice)
        await update.message.reply_text(f"Voice set to {voice}.")
    else:
        logging.info(f"Voice {voice} not found")
        await update.message.reply_text(f"Voice '{voice}' not found. Please try again.")


async def handle_tts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = get_user_session(update.effective_user.id)
    session.toggle_tts()
    if session.tts.is_active():
        await update.message.reply_text(TTS_ENABLED)
    else:
        await update.message.reply_text("TTS disabled.")


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = get_user_session(update.effective_user.id)
    session.toggle_image_session()
    if session.image_session:
        await update.message.reply_text("Your next prompt will render an image.")
    else:
        await update.message.reply_text("Image rendering canceled.")


async def handle_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = get_user_session(update.effective_user.id)
    session.reset()
    await update.message.reply_text("Session reset.")
