import logging

import openai
from telegram import Update, Message
from telegram.ext import ContextTypes, CallbackContext

from session import get_user_session

HELP_TEXT = """Hi! I'm a ChatGPT bot. I can answer your questions and reply to prompts.
    Try asking me a question – you can even record a voice note.
    If you forward me a voice note, I can summarize it for you.
    """


async def handle_text_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info(f"Received message: {update.message.text} from user {update.effective_user.id}")
    await handle_prompt(update, update.message.text)


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT)


async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = get_user_session(update)
    original_text = update.message.reply_to_message.text
    session.messages.append({"role": "assistant", "content": original_text})
    await handle_prompt(update, update.message.text)


async def handle_error(update: object, context: CallbackContext) -> None:
    logging.error(f"Update {update} caused error {context.error}")
    await update.message.reply_text("I'm very sorry, an error occured.")


async def handle_prompt(update: Update, prompt, msg: Message = None) -> None:
    if msg is None:
        msg = await update.message.reply_text("Thinking ...")
    else:
        await msg.edit_text("Thinking ...")
    session = get_user_session(update)
    session.messages.append({"role": "user", "content": prompt})

    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=session.messages
    )

    response = openai_response["choices"][0]["message"]["content"]
    session.messages.append({"role": "assistant", "content": response})
    await msg.edit_text(text=response)
