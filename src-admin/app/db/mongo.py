from pymongo import MongoClient
from pymongo.database import Database
import os

# Global variables to hold the MongoDB client and database instance
# These will be initialized once at application startup.
_mongo_client: MongoClient = None
_mongo_db: Database = None

def connect_to_mongo():
    """Initializes the MongoDB connection."""
    global _mongo_client, _mongo_db
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "impact_vibe_coder")
    try:
        _mongo_client = MongoClient(MONGO_URI)
        _mongo_db = _mongo_client[MONGO_DB_NAME]
        print(f"Connected to MongoDB database: {_mongo_db.name}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        # Optionally re-raise or handle this error more gracefully
        raise

def close_mongo_connection():
    """Closes the MongoDB connection."""
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
        _mongo_db = None
        print("MongoDB connection closed.")

def get_database() -> Database:
    """FastAPI dependency to provide a MongoDB database instance."""
    if _mongo_db is None:
        # This case should ideally not be hit if connect_to_mongo is called at startup.
        # It could indicate an issue with startup order or direct function call.
        raise Exception("MongoDB database not initialized. Please ensure connect_to_mongo() is called.")
    return _mongo_db