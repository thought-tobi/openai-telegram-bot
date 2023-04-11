import logging
import os
import uuid

import openai
import requests
from telegram import Update
from telegram.ext import ContextTypes, CallbackContext

from src.handlers.edit_message import EditMessage
from src.session.message import Message, USER, ASSISTANT
from src.session.prompts import SYSTEM_UNABLE_TO_RESPOND
from src.session.session import get_user_session, Session
from src.tts.text_to_speech import tts


async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = get_user_session(update.effective_user.id)
    original_text = update.message.reply_to_message.text
    session.messages.append(Message(role=ASSISTANT, content=original_text))
    session.save()
    await handle_prompt(update, update.message.text)


async def handle_error(update: object, context: CallbackContext) -> None:
    logging.error(f"Update {update} caused error {context.error}")
    await update.message.reply_text("I'm very sorry, an error occured.")
    raise context.error


async def handle_text_message(update: Update, _) -> None:
    logging.info(f"Received message from {update.effective_user.id}: {update.message.text}")
    await handle_prompt(update, update.message.text)


async def handle_prompt(update: Update, prompt, msg: EditMessage = None) -> None:
    if msg is None:
        msg = EditMessage(await update.message.reply_text("Thinking ..."))

    # retrieve user session and append prompt
    session = get_user_session(update.effective_user.id)
    message = Message(role=USER, content=prompt)
    session.add_message(message)
    logging.info(f"Effective prompt: {session.get_messages()[-1]}")

    if session.is_image_session_active():
        return await handle_text_to_image(session, update)

    # get chatgpt response
    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=session.get_messages()
    )

    response = openai_response["choices"][0]["message"]["content"]
    session.add_message(Message(role=ASSISTANT, content=response))
    logging.info(f"Response: {response}")
    await send_response(session, response, update, msg)


async def send_response(session: Session, response: str, update: Update, msg: EditMessage):
    if should_perform_tts(response, session):
        try:
            await msg.message.edit_text("Converting response to speech ...")
            tts_file = tts(response, session)
            await update.message.reply_voice(voice=open(tts_file, "rb"))
            os.remove(tts_file)
        except RuntimeError as e:
            logging.error("Failed to retrieve TTS, reason: " + str(e))
            session.deactivate_tts()
            await msg.message.edit_text(f"Unfortunately there was an error retrieving the TTS. "
                                        f"Your text response is below. TTS will be disabled for now.\n{response}")
    else:
        await msg.message.edit_text(msg.replace(response))


def should_perform_tts(response, session):
    # try to determine if chatgpt refused to answer the prompt as intended
    return session.tts.is_active() \
           and SYSTEM_UNABLE_TO_RESPOND.lower() not in response.lower() \
           and "as an ai language model" not in response.lower()


async def handle_text_to_image(session: Session, update: Update) -> None:
    prompt = session.get_messages()[-1]["content"]
    openai_response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = openai_response['data'][0]['url']
    await update.message.reply_photo(photo=image_url)
