from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Session:
    user_id: int
    created_at: datetime
    messages: list[dict]

    def __post_init__(self):
        self.expires_at = self.created_at + timedelta(minutes=30)
