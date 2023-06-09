from telegram import Update

from src.session.session import get_user_session


async def handle_start(update: Update, _) -> None:
    await update.message.reply_voice(voice=open("assets/start.mp3", "rb"))


async def handle_reset(update: Update, _) -> None:
    session = get_user_session(update.effective_user.id)
    session.reset()
    await update.message.reply_text("Session reset.")
