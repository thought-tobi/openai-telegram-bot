import logging

from telegram import Update

from src.handlers.base_handler import handle_prompt
from src.handlers.edit_message import EditMessage
from src.session.prompts import SUMMARY_PROMPT

async def handle_forwarded(update: Update, _) -> None:
    logging.info(f"Received forwarded message from user {update.effective_user.id}")
    msg = await update.message.reply_text("Thinking ...")
    prompt = SUMMARY_PROMPT + update.message.text
    await handle_prompt(update, prompt, EditMessage(msg))


async def handle_text_message(update: Update, _) -> None:
    logging.info(f"Received message from {update.effective_user.id}: {update.message.text}")
    await handle_prompt(update, update.message.text)
