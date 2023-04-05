from data.session import Session, create_new_session, get_user_session
import mongo
from unittest import TestCase


class TestSession(TestCase):

    # def setUp(self) -> None:
    #     mongo.init()

    def tearDown(self) -> None:
        mongo.delete_all()
        mongo.mongo_client.drop_database("sessions")

    def test_should_persist_session(self):
        user_id = 123
        session = create_new_session(user_id)
        assert get_user_session(user_id) == session
