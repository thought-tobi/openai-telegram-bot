from dataclasses import dataclass
import tiktoken


@dataclass
class Message:
    role: str
    content: str

    def __post_init__(self):
        self.tokens = self.calculate_tokens()

    def dict(self):
        return {
            "role": self.role,
            "content": self.content,
        }

    def calculate_tokens(self, model="gpt-3.5-turbo-0301"):
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(self.content))
