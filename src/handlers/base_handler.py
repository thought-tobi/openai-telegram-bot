import logging
import os

from telegram import Update

from src.client.chat import chat_completion
from src.handlers.edit_message import EditMessage
from src.session.message import Message, USER
from src.session.session import get_user_session, Session


async def handle_prompt(update: Update, prompt, msg: EditMessage = None) -> None:
    if msg is None:
        msg = EditMessage(await update.message.reply_text("Thinking ..."))

    # retrieve user session and append prompt
    session = get_user_session(update.effective_user.id)
    message = Message(role=USER, content=prompt)
    session.add_message(message)
    logging.info(f"Effective prompt: {session.messages[-1]}")

    response = await chat_completion(session.messages)

    session.add_message(response)
    logging.info(f"Response: {response}")
    await msg.message.edit_text(msg.replace(response.content))

