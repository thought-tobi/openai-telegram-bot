import datetime
import logging
import random
from typing import Optional
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

import openai
from pymongo.errors import CollectionInvalid
from telegram import Update, Message, User, Chat

from src.handlers.text_handlers import handle_text_message
from src.session import mongo
from src.session.message import USER, SYSTEM
from src.session.session import get_user_session

MOCK_GPT35_RESPONSE = {
    "choices": [
        {
            "finish_reason": "stop",
            "index": 0,
            "message": {
                "content": "Answer in the style of Donald Trump: This is the greatest Hello World ever!",
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

chat = Chat(123, "some-chat")
user = User(123, "some-user", False)
message = Message(message_id=456,
                  date=datetime.datetime.now(),
                  chat=chat,
                  text="some-message", from_user=user)
# user is internally extracted via message.from_user
update = Update(update_id=789, message=MagicMock())


# class TestIntegration(IsolatedAsyncioTestCase):
class IgnoreTest():

    def setUp(self) -> None:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        try:
            mongo.init()
        except CollectionInvalid:
            pass  # already initialized

    def tearDown(self) -> None:
        mongo.delete_all()
        mongo.mongo_client.drop_database("sessions")

    async def test_should_call_chatpgt(self):
        # given
        openai.Completion.create = MagicMock()

        # when
        await handle_text_message(update, None)

        # then
        # session created and message added
        self.assertEqual(SYSTEM, get_user_session(123).messages[0].role)
        self.assertEqual(USER, get_user_session(123).messages[1].role)
        self.assertEqual("hello", get_user_session(123).messages[1].content)

        # openai called
        openai.Completion.create.assert_called_once()
