import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from telegram import Update

SESSIONS = []

SYSTEM_PROMPT = """
    You are a telegram bot interfacing with ChatGPT. Your capabilities are as follows:
    - Answer user prompts
    - Understand user voice memos and answer their questions
    - Summarise forwarded voice memos
"""


@dataclass
class Session:
    user_id: int
    created_at: datetime
    messages: list[dict]

    def __post_init__(self):
        self.expires_at = self.created_at + timedelta(minutes=30)


def get_user_session(update: Update) -> Session:
    user_id = update.effective_user.id
    for session in SESSIONS:
        if session.user_id == user_id:
            if session.expires_at > datetime.now(timezone.utc):
                logging.info(f"Session for user {user_id} found")
                return session
            # also manages session, should probably be in a separate function
            else:
                logging.info(f"Session for user {user_id} expired, removing it from the list")
                SESSIONS.remove(session)
    return _create_new_session(update)


def _create_new_session(update: Update) -> Session:
    session = Session(user_id=update.effective_user.id,
                      created_at=update.message.date,
                      messages=[{"role": "system", "content": SYSTEM_PROMPT}])
    SESSIONS.append(session)
    logging.info(f"Created new session for user {update.effective_user.id}")
    return session
