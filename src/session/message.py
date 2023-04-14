from dataclasses import dataclass, asdict

import tiktoken

USER = "user"
ASSISTANT = "assistant"
SYSTEM = "system"


@dataclass
class Message:
    role: str
    content: str

    def calculate_tokens(self, model="gpt-3.5-turbo-0301"):
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(self.content))

    def asdict(self) -> dict:
        return asdict(self)
