import logging

from telegram import Update

from src.client.chat import chat_completion
from src.client.tts.elevenlabs import VOICES as ELEVEN_LABS_VOICES
from src.session.message import USER, Message
from src.session.prompts import PROMPT_IDEAS_PROMPT
from src.session.session import get_user_session

PROMPT_IDEAS_PLACEHOLDER = "..."

# displayed with the /help command
HELP_TEXT = f"""Hi! I'm a ChatGPT bot. I can answer your questions and reply to prompts.
- Try asking me a question – you can even record a voice note.
- Forward me a voice note to have it summarised.
- Type /tts to enable text-to-speech. I will read out my responses.
- Type /reset to have me forget our previous interactions.
Prompt ideas:
{PROMPT_IDEAS_PLACEHOLDER}
I'm also Open Source! Find me here:
https://github.com/thought-tobi/openai-telegram-bot
    """

# displayed when the user enables text-to-speech
TTS_ENABLED = "TTS enabled. I will read out my responses. " \
              "Disable with /tts or by waiting until your session expires [default: 5 minutes]."


async def handle_help(update: Update, _) -> None:
    msg = await update.message.reply_text(HELP_TEXT)
    prompt_suggestions = await chat_completion([Message(role=USER, content=PROMPT_IDEAS_PROMPT)])
    await msg.edit_text(msg.text.replace(PROMPT_IDEAS_PLACEHOLDER, prompt_suggestions.content))


async def handle_voice(update: Update, _) -> None:
    voice = update.message.text.replace("/voice ", "").lower()
    logging.info(voice)
    if voice in ELEVEN_LABS_VOICES:
        session = get_user_session(update.effective_user.id)
        session.set_voice(voice)
        await update.message.reply_text(f"Voice set to {voice}.")
    else:
        logging.info(f"Voice {voice} not found")
        await update.message.reply_text(f"Voice '{voice}' not found. Please try again.")


async def handle_tts(update: Update, _) -> None:
    session = get_user_session(update.effective_user.id)
    session.toggle_tts()
    if session.tts.is_active():
        await update.message.reply_text(TTS_ENABLED)
    else:
        await update.message.reply_text("TTS disabled.")


async def handle_image(update: Update, _) -> None:
    session = get_user_session(update.effective_user.id)
    session.toggle_image_session()
    if session.image_session:
        await update.message.reply_text("Your next prompt will render an image.")
    else:
        await update.message.reply_text("Image rendering canceled.")


async def handle_reset(update: Update, _) -> None:
    session = get_user_session(update.effective_user.id)
    session.reset()
    await update.message.reply_text("Session reset.")
