from telegram import Update
from telegram.ext import ContextTypes
from session import get_user_session
import openai
import logging


async def handle_text_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info(f"Received message: {update.message.text} from user {update.effective_user.id}")
    # send placeholder response
    msg = await update.message.reply_text("Thinking...")

    session = get_user_session(update)
    session.messages.append({"role": "user", "content": update.message.text})

    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=session.messages
    )

    text = openai_response["choices"][0]["message"]["content"]
    session.messages.append({"role": "assistant", "content": text})
    logging.info(session)
    await msg.edit_text(text=text)


async def handle_voice_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info(f"Received voice note from user {update.effective_user.id}")
    audio_file = context.bot.get_file(update.message.voice.file_id)
    # download the voice note as a file
    audio_file.download(f"{update.message.id}-voice_note.ogg")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    await update.message.reply_text(transcript)
