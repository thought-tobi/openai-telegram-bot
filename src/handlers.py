from telegram import Update
from telegram.ext import ContextTypes, CallbackContext
from session import get_user_session
import openai
from pydub import AudioSegment
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


async def handle_voice_note(update: Update, context: CallbackContext) -> None:
    logging.info(f"Received voice note from user {update.effective_user.id}")
    filename = f"tmp/{update.message.id}-voice_note"
    # download audio and convert it to mp3
    audio_file = await context.bot.get_file(update.message.voice.file_id)
    await audio_file.download_to_drive(f"{filename}.ogg")
    AudioSegment.from_file(f"{filename}.ogg").export(f"{filename}.mp3")
    # transcribe and return
    transcript = openai.Audio.transcribe("whisper-1", open(f"{filename}.mp3", "rb"))
    await update.message.reply_text(transcript["text"].encode().decode('utf-8'))
