import logging
import os

import openai
from pydub import AudioSegment
from telegram import Update
from telegram.ext import ContextTypes, CallbackContext

from session import get_user_session


async def handle_text_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info(f"Received message: {update.message.text} from user {update.effective_user.id}")
    await handle_prompt(update)


async def handle_voice_note(update: Update, context: CallbackContext) -> None:
    logging.info(f"Received voice note from user {update.effective_user.id}")
    transcript = await extract_text_from_audio(update, context)
    update.message.text = transcript
    await handle_prompt(update)


async def handle_prompt(update: Update) -> None:
    msg = await update.message.reply_text("Thinking...")
    session = get_user_session(update)
    session.messages.append({"role": "user", "content": update.message.text})

    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=session.messages
    )

    response = openai_response["choices"][0]["message"]["content"]
    session.messages.append({"role": "assistant", "content": response})
    await msg.edit_text(text=response)


async def extract_text_from_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    filename = f"./tmp/{update.message.id}-voice_note"
    # download audio and convert it to mp3
    audio_file = await context.bot.get_file(update.message.voice.file_id)
    await audio_file.download_to_drive(f"{filename}.ogg")
    AudioSegment.from_file(f"{filename}.ogg").export(f"{filename}.mp3")
    transcript = openai.Audio.transcribe("whisper-1", open(f"{filename}.mp3", "rb"))["text"].encode().decode('utf-8')
    # cleanup
    os.remove(f"{filename}.ogg")
    os.remove(f"{filename}.mp3")
    return transcript


def is_prompt(transcript: str) -> object:
    # contains deals with punctuation
    return transcript.split(" ")[0].lower().__contains__("prompt")
