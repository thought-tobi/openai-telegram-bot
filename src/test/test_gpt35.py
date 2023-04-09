import openai
from unittest import TestCase
from unittest.mock import MagicMock

from src.data.message import Message, USER, ASSISTANT
from src.data.session import create_new_session
import src.data.mongo as mongo
from pymongo.errors import CollectionInvalid

MOCK_RESPONSE = {
    "choices": [
        {
            "finish_reason": "stop",
            "index": 0,
            "message": {
                "content": "Hello back!",
                "role": "assistant"
            }
        }
    ],
    "created": 1680787848,
    "id": "chatcmpl-72JzMQVIyKqvJpxqwYA9XUivmSjag",
    "model": "gpt-3.5-turbo-0301",
    "object": "chat.completion",
    "usage": {
        "completion_tokens": 3,
        "prompt_tokens": 3,
        "total_tokens": 6
    }
}


class TestGPT(TestCase):

    def setUp(self):
        try:
            mongo.init()
        except CollectionInvalid:
            pass  # already initialized

    def tearDown(self) -> None:
        mongo.delete_all()
        mongo.mongo_client.drop_database("sessions")

    def test_should_reply_with_special_phrase_when_unable_to_perform_task(self):
        # when
        openai.ChatCompletion.create = MagicMock(return_value=MOCK_RESPONSE)
        user_id = 123
        session = create_new_session(user_id)
        # remove system prompt
        session.messages = []
        session.add_message(Message(role=USER, content="Hello World!"))

        # get chatgpt response
        openai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=session.get_messages()
        )

        session.add_message(Message(role=ASSISTANT, content=openai_response["choices"][0]["message"]["content"]))
        assert session.total_tokens() == 6
