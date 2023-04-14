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


# generates example prompts for the /help command
# "forget everything" so the previous prompts does not affect the outcome of this prompt.
PROMPT_IDEAS_PROMPT = "Generate three prompts with less than ten words each." \
              "Two prompts should showcase ChatGPT's ability to help with day-to-day problems." \
              "One should be funny, random, or quirky. Give me just the ideas, nothing else."
