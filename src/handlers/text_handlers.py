import logging
import os

import openai
from telegram import Update

from src.handlers.edit_message import EditMessage
from src.session.message import Message, USER, ASSISTANT
from src.session.prompts import SYSTEM_UNABLE_TO_RESPOND
from src.session.session import get_user_session, Session
from src.client.tts.text_to_speech import tts
from src.client.chat import chat_completion
from src.client.image import create_image


async def handle_reply(update: Update, _) -> None:
    session = get_user_session(update.effective_user.id)
    original_text = update.message.reply_to_message.text
    session.messages.append(Message(role=ASSISTANT, content=original_text))


async def handle_text_message(update: Update, _) -> None:
    logging.info(f"Received message from {update.effective_user.id}: {update.message.text}")
    # retrieve and prepare user session
    session = get_user_session(update.effective_user.id)
    session.add_message(Message(role=USER, content=update.message.text))
    # get and return response
    response = await chat_completion(session.messages)
    session.add_message(response)
    await update.message.reply_text(response.content)


async def handle_prompt(update: Update, prompt, msg: EditMessage = None) -> None:
    if msg is None:
        msg = EditMessage(await update.message.reply_text("Thinking ..."))

    # retrieve user session and append prompt
    session = get_user_session(update.effective_user.id)
    message = Message(role=USER, content=prompt)
    session.add_message(message)
    logging.info(f"Effective prompt: {session.messages[-1]}")

    if session.image_session:
        return await handle_text_to_image(session, update, msg)

    # get chatgpt response
    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=session.messages
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


async def handle_text_to_image(session: Session, update: Update, msg: EditMessage) -> None:
    session.toggle_image_session()
    prompt = session.messages[-1].content

    urls = create_image(prompt, 1)
    logging.info(f"Image URLs: {urls}")
    await msg.message.edit_text("Here is your image:")
    for url in urls:
        await update.message.reply_photo(photo=url)
