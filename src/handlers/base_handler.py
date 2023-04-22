import logging
import os

from telegram import Update

from src.client.chat import chat_completion
from src.client.image import create_image
from src.client.tts.text_to_speech import tts
from src.handlers.edit_message import EditMessage
from src.session.message import Message, USER
from src.session.prompts import SYSTEM_UNABLE_TO_RESPOND
from src.session.session import get_user_session, Session


# todo this appears to now be the base method for handling everything else
# maybe the mechanism for determining what to do should be something like session.get_action()??
async def handle_prompt(update: Update, prompt, msg: EditMessage = None) -> None:
    if msg is None:
        msg = EditMessage(await update.message.reply_text("Thinking ..."))

    # retrieve user session and append prompt
    session = get_user_session(update.effective_user.id)
    session.add_message(Message(role=USER, content=prompt))
    # todo make message modification more transparent
    logging.info(f"Effective prompt: {session.messages[-1]}")

    if session.image_session:
        return await handle_text_to_image(session, update, msg)

    response = await chat_completion(session.messages)

    session.add_message(response)
    logging.info(f"Response: {response}")
    await send_response(session, response.content, update, msg)


async def send_response(session: Session, response: str, update: Update, msg: EditMessage):
    if should_perform_tts(response, session):
        await msg.message.edit_text("Converting response to speech ...")
        tts_file = tts(response, session)
        await update.message.reply_voice(voice=open(tts_file, "rb"))
        os.remove(tts_file)
    else:
        await msg.message.edit_text(msg.replace(response))


async def handle_text_to_image(session: Session, update: Update, msg: EditMessage) -> None:
    session.toggle_image_session()
    prompt = session.messages[-1].content

    urls = create_image(prompt, session.image_count)
    logging.info(f"Image URLs: {urls}")
    await msg.message.edit_text("Here is your image:")
    for url in urls:
        await update.message.reply_photo(photo=url)


def should_perform_tts(response, session):
    # try to determine if chatgpt refused to answer the prompt as intended
    return session.tts.is_active() \
           and SYSTEM_UNABLE_TO_RESPOND.lower() not in response.lower() \
           and "as an ai language model" not in response.lower()
