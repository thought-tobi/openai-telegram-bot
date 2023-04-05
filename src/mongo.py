from dataclasses import asdict

import pymongo
from src.data.session import Session

mongo_url = "mongodb://localhost:27017/"
mongo_client = pymongo.MongoClient(mongo_url)
sessions = mongo_client["sessions"]


def init() -> None:
    sessions.create_collection("sessions")
    root_session = None
    ...


def persist_session(session: Session) -> None:
    sessions.insert_one(asdict(session))


def get_session(user_id: int) -> Session | None:
    return sessions.find_one({"user_id": user_id})

