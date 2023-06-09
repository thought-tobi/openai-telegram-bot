from telegram import Update

from src.client.chat import chat_completion
from src.session.message import USER, Message
from src.session.prompts import PROMPT_IDEAS_PROMPT
from src.session.session import get_user_session

PROMPT_IDEAS_PLACEHOLDER = "..."

# displayed with the /help command
HELP_TEXT = f"""Hi! I'm a ChatGPT bot. I can answer your questions and reply to prompts.
- Try asking me a question – you can even record a voice note.
- Forward me a voice note to have it summarised.
- Type /tts to enable text-to-speech. I will read out my responses.
- Type /reset to have me forget our previous interactions.
Prompt ideas:
{PROMPT_IDEAS_PLACEHOLDER}
I'm also Open Source! Find me here:
https://github.com/thought-tobi/openai-telegram-bot
    """

# displayed when the user enables text-to-speech
TTS_ENABLED = "TTS enabled. I will read out my responses. " \
              "Disable with /tts or by waiting until your session expires [default: 5 minutes]."


async def handle_help(update: Update, _) -> None:
    msg = await update.message.reply_text(HELP_TEXT)
    prompt_suggestions = await chat_completion([Message(role=USER, content=PROMPT_IDEAS_PROMPT)], model="gpt-4")
    await msg.edit_text(msg.text.replace(PROMPT_IDEAS_PLACEHOLDER, prompt_suggestions.content))


async def handle_reset(update: Update, _) -> None:
    session = get_user_session(update.effective_user.id)
    session.reset()
    await update.message.reply_text("Session reset.")
