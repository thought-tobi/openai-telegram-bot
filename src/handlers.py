import logging
import os

import openai
from pydub import AudioSegment
from PIL import Image
from telegram import Update, Message
from telegram.ext import ContextTypes, CallbackContext

from session import get_user_session


async def handle_text_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info(f"Received message: {update.message.text} from user {update.effective_user.id}")
    await handle_prompt(update, update.message.text)


async def handle_voice_note(update: Update, context: CallbackContext) -> None:
    logging.info(f"Received voice note from user {update.effective_user.id}")
    msg = await update.message.reply_text("Transcribing voice memo ...")
    transcript = await extract_text_from_audio(update, context)
    session = get_user_session(update)
    if session.state.get("transcribe"):
        await msg.edit_text(transcript)
        session.state["transcribe"] = False
        return
    await handle_prompt(update, transcript, msg)


async def handle_photo(update: Update, context: CallbackContext) -> None:
    logging.info(f"Received image from user {update.effective_user.id} with caption {update.message.caption}")
    image = await context.bot.get_file(update.message.photo[-1].file_id)
    prompt = update.message.text
    filename = f"./tmp/{update.message.id}-image"
    await image.download_to_drive(f"{filename}.jpg")
    msg = await update.message.reply_text("Generating image ...")
    img = Image.open(f"{filename}.jpg")
    img.putalpha(255)
    img.save(f"{filename}.png")
    logging.info(f"Getting suggestions from OpenAI API for image {filename}.png")
    response = openai.Image.create_edit(
        image=open(f"{filename}.png", "rb"),
        prompt=update.message.caption,
        n=1,
        size="512x512"
    )
    await msg.edit_text(response['data'][0]['url'])


async def handle_transcription_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = get_user_session(update)
    session.state["transcribe"] = True
    await update.message.reply_text("Ready to transcribe a voice note!")


async def handle_prompt(update: Update, prompt, msg: Message = None) -> None:
    if msg is None:
        msg = await update.message.reply_text("Thinking ...")
    else:
        await msg.edit_text("Thinking ...")
    session = get_user_session(update)
    session.messages.append({"role": "user", "content": prompt})

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
