from dataclasses import dataclass
import datetime

IMAGE_SESSION_LENGTH = 60


@dataclass
class ImageSession:
    enabled_until: datetime.datetime = datetime.datetime(1970, 1, 1)

    def reset(self):
        self.enabled_until = datetime.datetime(1970, 1, 1)

    def activate(self, session_length: int):
        self.enabled_until = datetime.datetime.now() + datetime.timedelta(seconds=session_length)

    def is_active(self) -> bool:
        return self.enabled_until > datetime.datetime.now()
