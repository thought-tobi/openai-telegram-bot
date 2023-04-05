import logging
from dataclasses import dataclass
import src.mongo as mongo

SESSION_LENGTH_MINUTES = 60

SYSTEM_PROMPT = """
    You are a telegram bot interfacing with ChatGPT. Your capabilities are as follows:
    - Answer user prompts
    - Understand user voice memos and answer their questions
    - Summarise forwarded voice memos
    - Use text-to-speech to read out your responses
    When asked questions about yourself, refer to the /help command for more information.
"""


@dataclass
class Session:
    user_id: int
    messages: list[dict]
    tts: bool = False
    current_voice: str = "bella"


def get_user_session(user_id: int) -> Session:
    session = mongo.get_session(user_id)
    if session is None:
        return create_new_session(user_id)


def create_new_session(user_id: int) -> Session:
    session = Session(user_id=user_id,
                      messages=[{"role": "system", "content": SYSTEM_PROMPT}])
    logging.info(f"Created new session for user {user_id}")
    mongo.persist_session(session)
    return session
