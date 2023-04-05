import time
from dataclasses import asdict
import sys
import os
from src.data.session import create_new_session, get_user_session, new_tts
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
        session.messages.append({"role": "user", "content": "hello world"})
        mongo.update_session(asdict(session))
        assert len(get_user_session(user_id).messages) == 2

    def test_should_update_tts(self):
        user_id = 123
        session = create_new_session(user_id)
        assert session.tts.is_active() is False
        session.tts = new_tts(2)
        mongo.update_session(asdict(session))
        assert get_user_session(user_id).tts.is_active() is True

        # expires
        time.sleep(3)
        assert get_user_session(user_id).tts.is_active() is False
