import datetime
from dataclasses import dataclass

TTS_SESSION_LENGTH = 300


@dataclass
class TTS:
    voice: str
    enabled_until: datetime.datetime

    @staticmethod
    def create_inactive():
        # create datetime of start of unix time
        return TTS(voice="bella", enabled_until=datetime.datetime(1970, 1, 1))

    def activate(self, session_length: int = TTS_SESSION_LENGTH):
        self.enabled_until = datetime.datetime.now() + datetime.timedelta(seconds=session_length)

    def is_active(self) -> bool:
        return self.enabled_until > datetime.datetime.now()
