import logging
from dataclasses import dataclass, asdict
from typing import List

import dacite

import src.session.mongo as mongo
from src.session.message import Message, SYSTEM
from src.session.prompts import SYSTEM_PROMPT

# should be 4096, but tiktoken seems to be calculating tokens differently than openai's current gpt3.5 implementation
# this adds some buffer as to not run into any errors
MAX_SESSION_SIZE = 3072


@dataclass
class Session:
    user_id: int
    messages: List[Message]

    def save(self) -> None:
        logging.info(f"Saving session state for user {self.user_id}")
        mongo.update_session(asdict(self))

    def add_message(self, message: Message) -> None:
        logging.info(f"Adding message {message} to session {self.user_id}")
        self.messages.append(message)
        while self.total_tokens() > MAX_SESSION_SIZE:
            # start at one to retain system prompt
            logging.info(f"Removing message {self.messages[1]} to keep total token count below {MAX_SESSION_SIZE}")
            self.messages.pop(1)
        self.save()

    def total_tokens(self) -> int:
        return sum(message.calculate_tokens() for message in self.messages)

    def reset(self) -> None:
        self.messages = [Message(role=SYSTEM, content=SYSTEM_PROMPT)]
        self.save()


def get_user_session(user_id: int) -> Session:
    session = mongo.get_session(user_id)
    if session is not None:
        logging.info(f"Found session for user {user_id}")
        return dacite.from_dict(data_class=Session, data=session)
    else:
        return create_new_session(user_id)


def create_new_session(user_id: int) -> Session:
    session = Session(user_id=user_id, messages=[Message(role=SYSTEM, content=SYSTEM_PROMPT)])
    logging.info(f"Created new session for user {user_id}")
    mongo.persist_session(asdict(session))
    return session
