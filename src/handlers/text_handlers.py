import logging
import os

import openai
from telegram import Update
from telegram.ext import ContextTypes, CallbackContext

from src.data.session import get_user_session
from src.data.edit_message import EditMessage
from src.text_to_speech import text_to_speech


async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = get_user_session(update.effective_user.id)
    original_text = update.message.reply_to_message.text
    session.messages.append({"role": "assistant", "content": original_text})
    session.save()
    await handle_prompt(update, update.message.text)


async def handle_error(update: object, context: CallbackContext) -> None:
    logging.error(f"Update {update} caused error {context.error}")
    await update.message.reply_text("I'm very sorry, an error occured.")


async def handle_prompt(update: Update, prompt, msg: EditMessage = None) -> None:
    if msg is None:
        msg = EditMessage(await update.message.reply_text("Thinking ..."))

    # retrieve user session and append prompt
    session = get_user_session(update.effective_user.id)
    session.messages.append({"role": "user", "content": prompt})
    logging.info(f"Effective prompt: {prompt}")

    # get chatgpt response
    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=session.messages
    )

    response = openai_response["choices"][0]["message"]["content"]
    session.messages.append({"role": "assistant", "content": response})
    logging.info(f"Response: {response}")
    session.save()
    # tts conversion and error handling
    if session.tts.is_active():
        try:
            tts_file = text_to_speech(response, session.tts.voice)
            await update.message.reply_voice(voice=open(tts_file, "rb"))
            os.remove(tts_file)
        except RuntimeError as e:
            logging.error("Failed to retrieve TTS, reason: " + str(e))
            session.tts = False
            await msg.message.edit_text(f"Unfortunately there was an error retrieving the TTS. "
                                        f"Your text response is below. TTS will be disabled for now.\n{response}")
    else:
        await msg.message.edit_text(msg.replace(response))
