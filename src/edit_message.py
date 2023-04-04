from dataclasses import dataclass
from telegram import Message
import re


@dataclass
class EditMessage:
    message: Message
    replace_pattern: str = None

    def replace(self, text: str) -> str:
        if self.replace_pattern is None:
            return text
        else:
            return self.message.text.replace(self.replace_pattern, text)
