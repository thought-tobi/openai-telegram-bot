from dataclasses import dataclass
from session import Session
from telegram import Update, Message


@dataclass
class Data:
    session: Session
    base_msg: Message = None
    update: Update = None
    text: str = None
