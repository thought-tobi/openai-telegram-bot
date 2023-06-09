import logging
import os

from dotenv import load_dotenv
from telegram import Update

from src.client.chat import chat_completion
from src.client.elevenlabs import tts
from src.handlers.edit_message import EditMessage
from src.session.message import Message, USER
from src.session.prompts import SYSTEM_UNABLE_TO_RESPOND
from src.session.session import get_user_session

load_dotenv()
voice_name = os.getenv("VOICE_NAME").replace("_", " ")
voice_id = os.getenv("VOICE_ID")


async def handle_prompt(update: Update, prompt, msg: EditMessage = None) -> None:
    if msg is None:
        msg = EditMessage(await update.message.reply_text("Thinking ..."))

    logging.info(f"Prompt: {prompt}")
    # retrieve user session and append prompt
    session = get_user_session(update.effective_user.id)
    message = Message(role=USER, content=enrich_prompt(prompt))
    session.add_message(message)

    response = await chat_completion(session.messages, "gpt-3.5-turbo")

    session.add_message(response)
    logging.info(f"Response: {response}")
    await send_response(response.content, update, msg)


def enrich_prompt(prompt) -> str:
    return f"Respond to the following prompt in the style of {voice_name}: {prompt}"


async def send_response(response: str, update: Update, msg: EditMessage):
    if should_perform_tts(response):
        await msg.message.edit_text("Converting response to speech ...")
        tts_file = tts(response, voice_id)
        await update.message.reply_voice(voice=open(tts_file, "rb"))
        os.remove(tts_file)
    else:
        # usually, if the ai fails to respond once, it's primed to keep doing so
        # send fallback, reset session
        await update.message.reply_voice(voice=open("assets/request_denied_2.mp3", "rb"))
        await update.message.reply_text(
            "Tip: ChatGPT has relatively heavy restrictions, particularly on political things. Here's a few things to try:"
            "- Don't say 'answer as Donald Trump' or anything like that. We handle that for you."
            "- Avoid overly political, violent or otherwise sensitive topics.")
        get_user_session(update.effective_user.id).reset()


def should_perform_tts(response):
    return SYSTEM_UNABLE_TO_RESPOND.lower() not in response.lower() \
        and "as an ai language model" not in response.lower()
