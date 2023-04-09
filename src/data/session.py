import logging
from dataclasses import dataclass, asdict
from typing import List, Dict

import dacite

import src.data.mongo as mongo
from src.data.message import Message
from src.data.tts import TTS, TTS_SESSION_LENGTH

SYSTEM_UNABLE_TO_RESPOND = "I cannot do that"
SYSTEM_PROMPT = f"""
    You are a telegram bot interfacing with ChatGPT. Your capabilities are as follows:
    - Answer user prompts
    - Understand user voice memos and answer their questions
    - Summarise forwarded voice memos
    - Use text-to-speech to read out your responses
    When asked questions about yourself, refer to the /help command for more information.
    If you cannot perform a task for any reason, reply exactly with '{SYSTEM_UNABLE_TO_RESPOND}', and follow up
    with a one-sentence explanation of why that is.
"""
# should be 4096, but tiktoken seems to be calculating tokens differently than openai's current gpt3.5 implementation
# this adds some buffer as to not run into any errors
MAX_SESSION_SIZE = 3072


@dataclass
class Session:
    user_id: int
    messages: List[Message]
    tts: TTS

    def save(self) -> None:
        logging.info(f"Saving session state for user {self.user_id}")
        mongo.update_session(asdict(self))

    def set_voice(self, voice) -> None:
        logging.info(f"Setting TTS voice for user {self.user_id} to {voice}")
        self.tts.voice = voice
        self.save()

    def toggle_tts(self) -> None:
        if self.tts.is_active():
            logging.info(f"Disabling TTS for user {self.user_id}")
            self.tts = TTS.create_inactive()
        else:
            logging.info(f"Enabling TTS for user {self.user_id}")
            self.tts.activate()
        self.save()

    def add_message(self, message: Message) -> None:
        if self.tts.is_active() and self.tts.voice != "bella":
            message.content = f"Answer in the style of {self.tts.voice}: {message.content}"
        self.messages.append(message)
        while self.total_tokens() > 4096:
            # start at one to retain system prompt
            logging.info(f"Removing message {self.messages[1]} to keep total token count below 4096")
            self.messages.pop(1)
        self.save()

    def get_messages(self) -> List[Dict]:
        return [message.dict() for message in self.messages]

    def activate_tts(self, session_length: int = TTS_SESSION_LENGTH) -> None:
        self.tts.activate(session_length)
        self.save()

    def reset_tts(self) -> None:
        self.tts = TTS.create_inactive()
        self.save()

    # this has the side effect of removing outdated tts sessions, may want to refactor
    def is_tts_active(self) -> bool:
        is_active = self.tts.is_active()
        if not is_active:
            self.reset_tts()
            self.save()
        return is_active

    def total_tokens(self) -> int:
        return sum(message.tokens for message in self.messages)


def get_user_session(user_id: int) -> Session:
    session = mongo.get_session(user_id)
    if session is not None:
        logging.info(f"Found session for user {user_id}")
        return dacite.from_dict(data_class=Session, data=session)
    else:
        return create_new_session(user_id)


def create_new_session(user_id: int) -> Session:
    session = Session(user_id=user_id,
                      messages=[Message(role="system", content=SYSTEM_PROMPT)],
                      tts=TTS.create_inactive())
    logging.info(f"Created new session for user {user_id}")
    mongo.persist_session(asdict(session))
    return session
