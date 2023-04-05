import datetime
import logging
from dataclasses import dataclass, asdict

import dacite

import src.data.mongo as mongo

TTS_SESSION_LENGTH = 5

SYSTEM_PROMPT = """
    You are a telegram bot interfacing with ChatGPT. Your capabilities are as follows:
    - Answer user prompts
    - Understand user voice memos and answer their questions
    - Summarise forwarded voice memos
    - Use text-to-speech to read out your responses
    When asked questions about yourself, refer to the /help command for more information.
"""


@dataclass
class TTS:
    voice: str
    enabled_until: datetime.datetime | None

    def is_active(self) -> bool:
        if self.session_expired():
            self.enabled_until = None
        return self.enabled_until is not None

    def session_expired(self) -> bool:
        return self.enabled_until is not None and self.enabled_until < datetime.datetime.now()


@dataclass
class Session:
    user_id: int
    messages: list[dict]
    tts: TTS

    def save(self):
        logging.info(f"Saving session state for user {self.user_id}")
        mongo.update_session(asdict(self))


def get_user_session(user_id: int) -> Session:
    session = mongo.get_session(user_id)
    if session is not None:
        logging.info(f"Found session for user {user_id}")
        return dacite.from_dict(data_class=Session, data=session)
    else:
        return create_new_session(user_id)


def create_new_session(user_id: int) -> Session:
    session = Session(user_id=user_id,
                      messages=[{"role": "system", "content": SYSTEM_PROMPT}],
                      tts=inactive_tts())
    logging.info(f"Created new session for user {user_id}")
    mongo.persist_session(asdict(session))
    return session


def inactive_tts() -> TTS:
    return TTS(voice="bella", enabled_until=None)


def new_tts() -> TTS:
    return TTS(voice="bella",
               enabled_until=datetime.datetime.now() + datetime.timedelta(minutes=TTS_SESSION_LENGTH))
