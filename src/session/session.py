import logging
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

import dacite

import src.session.mongo as mongo
from src.session.message import Message, USER, SYSTEM, ASSISTANT
from src.session.prompts import SYSTEM_PROMPT
from src.session.tts import TTS, TTS_SESSION_LENGTH, DEFAULT

# should be 4096, but tiktoken seems to be calculating tokens differently than openai's current gpt3.5 implementation
# this adds some buffer as to not run into any errors
MAX_SESSION_SIZE = 3072


@dataclass
class Session:
    user_id: int
    messages: List[Message]
    tts: TTS
    image_session: bool = False
    edit_image: bool = False

    def save(self) -> None:
        logging.info(f"Saving session state for user {self.user_id}")
        mongo.update_session(asdict(self))

    def set_voice(self, voice) -> None:
        logging.info(f"Setting TTS voice for user {self.user_id} to {voice}")
        self.tts.voice = voice
        self.save()

    def add_message(self, message: Message) -> None:
        # in case the prompt or the answer needs modification
        message = self.add_modifiers(message)
        message = self.cleanup(message)
        logging.info(f"Adding message {message} to session {self.user_id}")
        self.messages.append(message)
        while self.total_tokens() > MAX_SESSION_SIZE:
            # start at one to retain system prompt
            logging.info(f"Removing message {self.messages[1]} to keep total token count below {MAX_SESSION_SIZE}")
            self.messages.pop(1)
        self.save()

    @staticmethod
    def cleanup(message: Message) -> Message:
        content = message.content
        if message.role == ASSISTANT:
            # if chatgpt adds something like "answer in the style of <voice>:" to the response, remove it
            chatgpt_boilerplate = message.content.split(":")
            if len(chatgpt_boilerplate) > 1:
                content = chatgpt_boilerplate[1]
        return Message(message.role, content)

    # modify prompt to get more specific results
    def add_modifiers(self, message) -> Message:
        content = message.content
        if self.custom_voice_enabled(message):
            content = f"Respond to the following prompt in the style of {self.tts.voice}:" \
                      f"{message.content} " \
                      f"Be concise (three sentences max)."
        return Message(message.role, content)

    def custom_voice_enabled(self, message):
        return self.tts.is_active() and self.tts.voice is not DEFAULT and message.role == USER

    def total_tokens(self) -> int:
        return sum(message.tokens for message in self.messages)

    def get_messages(self) -> List[Dict]:
        return [message.dict() for message in self.messages]

    def toggle_tts(self) -> None:
        if self.tts.is_active():
            logging.info(f"Disabling TTS for user {self.user_id}")
            self.deactivate_tts()
        else:
            logging.info(f"Enabling TTS for user {self.user_id}")
            self.activate_tts()
        self.save()

    def toggle_image_session(self) -> None:
        if self.image_session:
            logging.info(f"Disabling image session for user {self.user_id}")
            self.image_session = False
        else:
            logging.info(f"Enabling image session for user {self.user_id}")
            self.image_session = True
        self.save()

    def start_image_edit_process(self):
        self.edit_image = True
        self.save()

    def stop_image_edit_process(self):
        self.edit_image = False
        self.save()

    # this has the side effect of removing outdated tts sessions, may want to refactor
    def is_tts_active(self) -> bool:
        is_active = self.tts.is_active()
        if not is_active:
            self.tts.reset()
            self.save()
        return is_active

    def activate_tts(self, length: int = TTS_SESSION_LENGTH) -> None:
        self.tts.activate(length)
        self.save()

    def deactivate_tts(self) -> None:
        self.tts.reset()
        self.save()

    def reset(self) -> None:
        self.messages = [Message(role=SYSTEM, content=SYSTEM_PROMPT)]
        self.tts.reset()
        self.edit_image = False
        self.save()


def get_user_session(user_id: int) -> Session:
    session = mongo.get_session(user_id)
    if session is not None:
        logging.info(f"Found session for user {user_id}")
        return dacite.from_dict(data_class=Session, data=session)
    else:
        return create_new_session(user_id)


def create_new_session(user_id: int) -> Session:
    session = Session(user_id=user_id,
                      messages=[Message(role=SYSTEM, content=SYSTEM_PROMPT)],
                      tts=TTS(),
                      image_session=False)
    logging.info(f"Created new session for user {user_id}")
    mongo.persist_session(asdict(session))
    return session
