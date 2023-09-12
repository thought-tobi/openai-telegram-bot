from typing import List

import openai

from src.session.message import Message, ASSISTANT


async def chat_completion(messages: List[Message]) -> Message:
    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[message.asdict() for message in messages]
    )
    return Message(role=ASSISTANT, content=openai_response["choices"][0]["message"]["content"])
