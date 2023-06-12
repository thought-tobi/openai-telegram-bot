import os

from dotenv import load_dotenv

load_dotenv()

# bot **should** reply with this message when it cannot perform a task.
# doesn't always work, may have to find a smarter way to do this.
SYSTEM_UNABLE_TO_RESPOND = "I cannot do that"

# system prompt that defines the general directive of the bot. message 0 of every session, never should be removed.
SYSTEM_PROMPT = f"""
    You are a Telegram bot, answering questions in the style of {os.environ["VOICE_NAME"]}. 
    Your goal is to be as convincing as possible.
    If you cannot answer a question, answer EXACTLY with "{SYSTEM_UNABLE_TO_RESPOND}".
"""
