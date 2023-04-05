import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.data.edit_message import EditMessage
from src.data.session import get_user_session, new_tts
from src.handlers.text_handlers import handle_prompt
from src.text_to_speech import voices

HELP_TEXT = """Hi! I'm a ChatGPT bot. I can answer your questions and reply to prompts.
- Try asking me a question – you can even record a voice note.
- If you forward me a voice note, I can summarize it for you.
- Type /tts to enable text-to-speech. I will read out my responses.
Prompt ideas:
...
I'm also Open Source! Find me here:
https://github.com/thought-tobi/openai-telegram-bot
    """

# hack to forget the session
PROMPT_HELP = "Forget everything." \
              "Generate three prompts with less than ten words each." \
              "Two prompts should showcase ChatGPT's ability to help with day-to-day problems." \
              "One should be funny, random, or quirky. Give me just the ideas, nothing else."

TTS_ENABLED = "TTS enabled. I will read out my responses. " \
              "Disable with /tts or by waiting until your session expires [default: 60 minutes]."


async def handle_text_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info(f"Received message: {update.message.text} from user {update.effective_user.id}")
    await handle_prompt(update, update.message.text)


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text(HELP_TEXT)
    await handle_prompt(update, PROMPT_HELP, EditMessage(msg, "..."))


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    voice = update.message.text.replace("/voice ", "").lower()
    if voice in voices:
        session = get_user_session(update.effective_user.id)
        session.tts.voice = voice
        logging.info(f"Setting TTS voice for user {update.effective_user.id}")
        session.save()
        await update.message.reply_text(f"Voice set to {voice}.")
    else:
        logging.info(f"Voice {voice} not found")
        await update.message.reply_text(f"Voice '{voice}' not found. Please try again.")


async def handle_tts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = get_user_session(update.effective_user.id)
    session.tts = new_tts()
    session.save()
    if session.tts:
        await update.message.reply_text(TTS_ENABLED)
    else:
        await update.message.reply_text("TTS disabled.")
