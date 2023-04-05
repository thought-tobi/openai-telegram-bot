import time
from src.data.session import create_new_session, get_user_session
from src.data import mongo
from unittest import TestCase


class TestSession(TestCase):

    def setUp(self) -> None:
        mongo.init()

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
        session.add_message({"role": "user", "content": "hello world"})
        assert len(get_user_session(user_id).messages) == 2

    def test_should_update_tts(self):
        user_id = 123
        session = create_new_session(user_id)
        assert session.tts.is_active() is False
        session.activate_tts(2)
        assert get_user_session(user_id).tts.is_active() is True

        # expires
        time.sleep(3)
        assert get_user_session(user_id).is_tts_active() is False

    def test_should_retain_voice_when_session_resets(self):
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
