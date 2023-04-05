import pymongo

mongo_url = "mongodb://localhost:27017/"
mongo_client = pymongo.MongoClient(mongo_url)
sessions_db = mongo_client["sessions"]
sessions = sessions_db["sessions"]


def init() -> None:
    sessions_db.create_collection("sessions")
    root_session = None
    ...


def persist_session(session: dict) -> None:
    sessions.insert_one(session)


def get_session(user_id: int) -> dict | None:
    return sessions.find_one({"user_id": user_id})


def delete_session(user_id: int) -> None:
    sessions.delete_one({"user_id": user_id})


def delete_all() -> None:
    sessions.delete_many({})
