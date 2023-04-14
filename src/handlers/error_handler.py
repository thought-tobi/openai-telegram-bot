import logging

from telegram.ext import CallbackContext


async def handle_error(update: object, context: CallbackContext) -> None:
    logging.error(f"Update {update} caused error {context.error}")
    await update.message.reply_text("I'm very sorry, an error occured. This bot is currently in development, so this"
                                    "is bound to happen. Try resetting your session by typing /reset. If the problem"
                                    "persists, contact @violin_tobi.")
    raise context.error
