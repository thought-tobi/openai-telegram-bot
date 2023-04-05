import logging
import os

import openai
from telegram import Update
from telegram.ext import ContextTypes, CallbackContext

from src.data.session import get_user_session
from src.data.edit_message import EditMessage
from src.text_to_speech import text_to_speech, voices

HELP_TEXT = """Hi! I'm a ChatGPT bot. I can answer your questions and reply to prompts.
- Try asking me a question – you can even record a voice note.
- If you forward me a voice note, I can summarize it for you.
- Type /tts to enable text-to-speech. I will read out my responses.
Prompt ideas:
...
I'm also Open Source! Find me here:
https://github.com/thought-tobi/openai-telegram-bot
    """

# hack to forget the session
PROMPT_HELP = "Forget everything." \
              "Generate three prompts with less than ten words each." \
              "Two prompts should showcase ChatGPT's ability to help with day-to-day problems." \
              "One should be funny, random, or quirky. Give me just the ideas, nothing else."

TTS_ENABLED = "TTS enabled. I will read out my responses. " \
              "Disable with /tts or by waiting until your session expires [default: 60 minutes]."


async def handle_text_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info(f"Received message: {update.message.text} from user {update.effective_user.id}")
    await handle_prompt(update, update.message.text)


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text(HELP_TEXT)
    await handle_prompt(update, PROMPT_HELP, EditMessage(msg, "..."))


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    voice = update.message.text.replace("/voice ", "").lower()
    if voice in voices:
        session = get_user_session(update.effective_user.id)
        session.current_voice = voice
        logging.info(f"Setting TTS voice for user {update.effective_user.id}")
        session.save()
        await update.message.reply_text(f"Voice set to {voice}.")
    else:
        logging.info(f"Voice {voice} not found")
        await update.message.reply_text(f"Voice '{voice}' not found. Please try again.")


async def handle_tts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = get_user_session(update.effective_user.id)
    session.tts = not session.tts
    session.save()
    if session.tts:
        await update.message.reply_text(TTS_ENABLED)
    else:
        await update.message.reply_text("TTS disabled.")


async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = get_user_session(update.effective_user.id)
    original_text = update.message.reply_to_message.text
    session.messages.append({"role": "assistant", "content": original_text})
    session.save()
    await handle_prompt(update, update.message.text)


async def handle_error(update: object, context: CallbackContext) -> None:
    logging.error(f"Update {update} caused error {context.error}")
    await update.message.reply_text("I'm very sorry, an error occured.")


async def handle_prompt(update: Update, prompt, msg: EditMessage = None) -> None:
    if msg is None:
        msg = EditMessage(await update.message.reply_text("Thinking ..."))

    # retrieve user session and append prompt
    session = get_user_session(update.effective_user.id)
    session.messages.append({"role": "user", "content": prompt})
    logging.info(f"Effective prompt: {prompt}")

    # get chatgpt response
    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=session.messages
    )

    response = openai_response["choices"][0]["message"]["content"]
    session.messages.append({"role": "assistant", "content": response})
    logging.info(f"Response: {response}")
    session.save()
    # tts conversion and error handling
    if session.tts:
        try:
            tts_file = text_to_speech(response, session.current_voice)
            await update.message.reply_voice(voice=open(tts_file, "rb"))
            os.remove(tts_file)
        except RuntimeError as e:
            logging.error("Failed to retrieve TTS, reason: " + str(e))
            session.tts = False
            await msg.message.edit_text(f"Unfortunately there was an error retrieving the TTS. "
                                        f"Your text response is below. TTS will be disabled for now.\n{response}")
    else:
        await msg.message.edit_text(msg.replace(response))
