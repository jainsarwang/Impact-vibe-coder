from pymongo import MonogoClient
from ..model.session_schema import session_schema
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["impact_vibe_coder"]
session_db = db["session"]

class SessionManager:
    @staticmethod
    async def set(session_id: str):
        """
        Set the session ID in the database.

        Args:
            session_id (str): The session ID to set.
        """
        session_data = {
            "session_id": session_id,
            "created_at": datetime.datetime.utcnow(),
            "checklist": []
        }
        await session_db.insert_one(session_data)

    @staticmethod
    async def get():
        """get the current session ID from the database.
        Returns:
            str: The current session ID.
        """
        session = await session_db.find_one({}, sort=[("created_at", -1)])
        if session:
            return session.get("session_id")
        return None