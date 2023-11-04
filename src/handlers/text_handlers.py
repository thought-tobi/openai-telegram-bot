import logging

from telegram import Update

from src.handlers.base_handler import handle_prompt, handle_translation
from src.handlers.edit_message import EditMessage
from src.session.prompts import SUMMARY_PROMPT


async def handle_forwarded(update: Update, _) -> None:
    logging.info(f"Received forwarded message from user {update.effective_user.id}")
    await handle_translation(update)


async def handle_text_message(update: Update, _) -> None:
    logging.info(f"Received message from {update.effective_user.id}: {update.message.text}")
    await handle_prompt(update)
