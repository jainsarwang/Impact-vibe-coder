from pymongo import MongoClient
from ..model.session_schema import session_schema
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import logging

client = MongoClient("mongodb://localhost:27017")
db = client["impact_vibe_coder"]
session_db = db["session"]

class SessionManager:
    @staticmethod
    def set(session_id: str):
        """
        Set the session ID in the database.

        Args:
            session_id (str): The session ID to set.
        """
        session_data = {
            "session_id": session_id,
            "created_at": datetime.now(),
            "checklist": []
        }
        logging.info(f"Setting session ID: {session_id}")
        session_db.insert_one(session_data)

    @staticmethod
    def get():
        """get the current session ID from the database.
        Returns:
            str: The current session ID.
        """
        session = session_db.find_one({}, sort=[("created_at", -1)])
        if session:
            logging.info(f"Retrieved session ID: {session.get('session_id')}")
            return session.get("session_id")
        return None