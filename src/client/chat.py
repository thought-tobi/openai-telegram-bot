from typing import List

import openai

from src.session.message import Message, ASSISTANT


async def chat_completion(messages: List[Message], model: str) -> Message:
    openai_response = openai.ChatCompletion.create(
        model=model,
        messages=[message.asdict() for message in messages]
    )
    return Message(role=ASSISTANT, content=openai_response["choices"][0]["message"]["content"])
