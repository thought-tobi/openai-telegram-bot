import logging

from telegram import Update

from src.handlers.base_handler import handle_prompt


async def handle_text_message(update: Update, _) -> None:
    logging.info(f"Received message from {update.effective_user.id}: {update.message.text}")
    await handle_prompt(update, update.message.text)
