import datetime
import logging
from dataclasses import dataclass, asdict

import dacite
from typing import Union, List, Dict

import src.data.mongo as mongo

TTS_SESSION_LENGTH = 300

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
    enabled_until: Union[datetime.datetime, None]

    @staticmethod
    def create_inactive():
        return TTS(voice="bella", enabled_until=None)

    def activate(self, session_length: int = TTS_SESSION_LENGTH):
        self.enabled_until = datetime.datetime.now() + datetime.timedelta(seconds=session_length)

    def is_expired(self):
        return self.enabled_until is not None and self.enabled_until < datetime.datetime.now()

    def is_active(self):
        return self.enabled_until is not None


@dataclass
class Session:
    user_id: int
    messages: List[Dict]
    tts: TTS

    def save(self):
        logging.info(f"Saving session state for user {self.user_id}")
        mongo.update_session(asdict(self))

    def set_voice(self, voice):
        logging.info(f"Setting TTS voice for user {self.user_id} to {voice}")
        self.tts.voice = voice
        self.save()

    def toggle_tts(self):
        if self.tts.is_active():
            logging.info(f"Disabling TTS for user {self.user_id}")
            self.tts.deactivate()
        else:
            logging.info(f"Enabling TTS for user {self.user_id}")
            self.tts.activate()
        self.save()

    def add_message(self, message: dict):
        self.messages.append(message)
        self.save()

    def activate_tts(self, session_length: int = TTS_SESSION_LENGTH):
        self.tts.activate(session_length)
        self.save()

    def reset_tts(self):
        self.tts = TTS.create_inactive()
        self.save()

    # this has the side effect of removing outdated tts sessions, may want to refactor
    def is_tts_active(self):
        if self.tts.enabled_until is not None:
            if self.tts.is_expired():
                self.reset_tts()
        self.save()
        return self.tts.is_active()


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
                      tts=TTS.create_inactive())
    logging.info(f"Created new session for user {user_id}")
    mongo.persist_session(asdict(session))
    return session
