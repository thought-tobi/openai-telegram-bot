# Bot prompts and prompt modifications, as well as help pages and other system messages.

# bot **should** reply with this message when it cannot perform a task.
# doesn't always work, may have to find a smarter way to do this.
SYSTEM_UNABLE_TO_RESPOND = "I cannot do that"

# system prompt that defines the general directive of the bot. message 0 of every session, never should be removed.
SYSTEM_PROMPT = f"""
    You are a telegram bot interfacing with ChatGPT. Your capabilities are as follows:
    - Answer user prompts
    - Understand user voice memos and answer their questions
    - Summarise forwarded voice memos
    - Use text-to-speech to read out your responses
    When asked questions about yourself, refer to the /help command for more information.
    If you cannot perform a task for any reason, reply EXACTLY with '{SYSTEM_UNABLE_TO_RESPOND}', and follow up
    with a one-sentence explanation of why that is.
"""

# displayed with the /help command
HELP_TEXT = """Hi! I'm a ChatGPT bot. I can answer your questions and reply to prompts.
- Try asking me a question – you can even record a voice note.
- Forward me a voice note to have it summarised.
- Type /tts to enable text-to-speech. I will read out my responses.
- Type /reset to have me forget our previous interactions.
Prompt ideas:
...
I'm also Open Source! Find me here:
https://github.com/thought-tobi/openai-telegram-bot
    """

# generates example prompts for the /help command
# "forget everything" so the previous prompts does not affect the outcome of this prompt.
PROMPT_HELP = "Forget everything." \
              "Generate three prompts with less than ten words each." \
              "Two prompts should showcase ChatGPT's ability to help with day-to-day problems." \
              "One should be funny, random, or quirky. Give me just the ideas, nothing else."


# displayed when the user enables text-to-speech
TTS_ENABLED = "TTS enabled. I will read out my responses. " \
              "Disable with /tts or by waiting until your session expires [default: 5 minutes]."
