import time
from unittest import TestCase

from pymongo.errors import CollectionInvalid

from src.data import mongo
from src.data.message import Message
from src.data.session import create_new_session, get_user_session


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
        session.add_message(Message(role="user", content="hello"))
        assert len(get_user_session(user_id).messages) == 2

    def test_should_expire_tts(self):
        user_id = 123
        session = create_new_session(user_id)
        assert session.tts.is_active() is False
        session.activate_tts(2)
        assert get_user_session(user_id).tts.is_active() is True

        # expires
        time.sleep(3)
        assert get_user_session(user_id).is_tts_active() is False

    def test_should_reset_voice_when_session_resets(self):
        user_id = 123
        session = create_new_session(user_id)
        session.tts.activate(2)
        session.set_voice("peterson")

        # get session
        assert get_user_session(user_id).tts.voice == "peterson"

        # session expires
        time.sleep(2)
        assert get_user_session(user_id).is_tts_active() is False
        assert get_user_session(user_id).tts.voice == "bella"

    def test_should_correctly_count_total_tokens(self):
        user_id = 123
        session = create_new_session(user_id)
        # remove system prompt
        session.messages.pop(0)
        session.add_message(Message(role="system", content="some message"))
        session.add_message(Message(role="user", content="hello"))
        assert session.total_tokens() == 3

    def test_should_delete_old_messages_if_tokens_exceed_4096(self):
        user_id = 123
        session = create_new_session(user_id)
        # remove system prompt
        session.messages.pop(0)

        session.add_message(Message(role="system", content="some system prompt"))
        session.add_message(Message(role="user", content="hello"))
        session.add_message(Message(role="assistant", content="hi"))

        assert session.total_tokens() == 5

        # add tokens to overflow threshold
        session.add_message(Message(role="user", content="hello" * 4093))

        # verify first message has been deleted and system prompt has been retained
        assert session.total_tokens() == 4096
        assert len(session.messages) == 2
        assert session.messages[0].role == "system"

        # add one more message
        session.add_message(Message(role="user", content="hi"))
        assert session.total_tokens() == 4
