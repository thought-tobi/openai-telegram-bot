import logging
import os

from telegram import Update
import src.client.lingolift as lingolift

from src.client.chat import chat_completion
from src.handlers.edit_message import EditMessage
from src.session.message import Message, USER
from src.session.session import get_user_session, Session


async def handle_prompt(update: Update) -> None:
    msg = EditMessage(await update.message.reply_text("Thinking ..."))
    prompt = update.message.text

    # retrieve user session and append prompt
    session = get_user_session(update.effective_user.id)
    message = Message(role=USER, content=prompt)
    session.add_message(message)
    logging.info(f"Effective prompt: {session.messages[-1]}")

    response = await chat_completion(session.messages)

    session.add_message(response)
    logging.info(f"Response: {response}")
    await msg.message.edit_text(msg.replace(response.content))


async def handle_translation(update: Update) -> None:
    msg = EditMessage(await update.message.reply_text("Thinking ..."))
    prompt = update.message.text

    response = await lingolift.get_all(prompt)

    logging.info(f"Response: {response}")
    await msg.message.edit_text(msg.replace(str(response)))
