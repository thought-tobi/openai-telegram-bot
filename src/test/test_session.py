import time
from unittest import TestCase

from pymongo.errors import CollectionInvalid

from src.session import mongo
from src.session.message import Message, SYSTEM, USER, ASSISTANT
from src.session.session import create_new_session, get_user_session, MAX_SESSION_SIZE
from src.session import tts


class TestSession(TestCase):

    def setUp(self) -> None:
        try:
            mongo.init()
        except CollectionInvalid:
            pass  # already initialized

    def tearDown(self) -> None:
        mongo.delete_all()
        mongo.mongo_client.drop_database("sessions")

    def test_should_persist_session(self):
        user_id = 123
        session = create_new_session(user_id)
        assert get_user_session(user_id) == session

    def test_should_update_session(self):
        user_id = 123
        session = create_new_session(user_id)
        assert len(get_user_session(user_id).messages) == 1
        session.add_message(Message(role=USER, content="hello"))
        assert len(get_user_session(user_id).messages) == 2

    def test_should_correctly_count_total_tokens(self):
        user_id = 123
        session = create_new_session(user_id)
        # remove system prompt
        session.messages.pop(0)
        session.add_message(Message(role=SYSTEM, content="some message"))
        session.add_message(Message(role=USER, content="hello"))
        assert session.total_tokens() == 3

    # these technically work, but tiktoken counts tokens differently than chatgpt as of 2023-04-09
    def test_should_delete_old_messages_if_tokens_exceed_4096(self):
        user_id = 123
        session = create_new_session(user_id)
        # remove system prompt
        session.messages.pop(0)

        session.add_message(Message(role=SYSTEM, content="some system prompt"))
        session.add_message(Message(role=USER, content="hello"))
        session.add_message(Message(role=ASSISTANT, content="hi"))

        assert session.total_tokens() == 5

        # add tokens to overflow threshold
        session.add_message(Message(role=USER, content="hello" * (MAX_SESSION_SIZE - 3)))

        # verify first message has been deleted and system prompt has been retained
        assert session.total_tokens() == MAX_SESSION_SIZE
        assert len(session.messages) == 2
        assert session.messages[0].role == SYSTEM

        # add one more message
        session.add_message(Message(role=USER, content="hi"))
        assert session.total_tokens() == 4

    def test_should_handle_reset(self):
        user_id = 123
        session = create_new_session(user_id)

        session.add_message(Message(role=SYSTEM, content="some system prompt"))
        session.add_message(Message(role=USER, content="hello"))
        session.add_message(Message(role=ASSISTANT, content="hi"))

        session.reset()

        # verify system prompt is still there
        assert len(session.messages) == 1
        assert session.messages[0].role == SYSTEM
