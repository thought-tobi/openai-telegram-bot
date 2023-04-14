import logging
import os

import openai
from pydub import AudioSegment
from telegram import Update
from telegram.ext import CallbackContext, ContextTypes

from src.handlers.base_handler import handle_prompt
from src.handlers.edit_message import EditMessage


async def handle_voice_note(update: Update, context: CallbackContext) -> None:
    logging.info(f"Received voice note from user {update.effective_user.id}")
    msg = await update.message.reply_text("Transcribing voice memo ...")
    transcript = await extract_text_from_audio(update, context)
    await msg.edit_text("Thinking ...")
    await handle_prompt(update, transcript, EditMessage(msg))


async def summarize_voice_note(update: Update, context: CallbackContext) -> None:
    logging.info(f"Received forwarded voice note from user {update.effective_user.id}")
    msg = await update.message.reply_text("Summarizing voice memo ...")
    transcript = await extract_text_from_audio(update, context)
    prompt = "Summarize the following text in its original language: " + transcript
    await msg.edit_text("Thinking ...")
    await handle_prompt(update, prompt, EditMessage(msg))


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
