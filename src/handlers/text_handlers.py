import logging

from telegram import Update

from src.handlers.base_handler import handle_prompt
from src.session.message import Message, ASSISTANT
from src.session.session import get_user_session


async def handle_reply(update: Update, _) -> None:
    session = get_user_session(update.effective_user.id)
    original_text = update.message.reply_to_message.text
    session.add_message(Message(role=ASSISTANT, content=original_text))
    await handle_prompt(update, update.message.text)


async def handle_text_message(update: Update, _) -> None:
    logging.info(f"Received message from {update.effective_user.id}: {update.message.text}")
    await handle_prompt(update, update.message.text)
