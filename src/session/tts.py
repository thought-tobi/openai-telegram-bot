import datetime
from dataclasses import dataclass

TTS_SESSION_LENGTH = 300

DEFAULT = ""


@dataclass
class TTS:
    enabled_until: datetime.datetime = datetime.datetime(1970, 1, 1)
    voice: str = DEFAULT

    def reset(self):
        self.voice = DEFAULT
        self.enabled_until = datetime.datetime(1970, 1, 1)

    def activate(self, session_length: int = TTS_SESSION_LENGTH):
        self.enabled_until = datetime.datetime.now() + datetime.timedelta(seconds=session_length)

    def is_active(self) -> bool:
        return self.enabled_until > datetime.datetime.now()
