
import logging
import os

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError

class Database:
    def __init__(self, connection_string, db_name):
        self.connection_string = connection_string
        self.db_name = db_name
        self.client = None
        self.db = None

    def connect(self):
        """Connects to MongoDB."""
        try:
            logging.info("Connecting to MongoDB...")
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.db_name]
            self.client.admin.command('ping')  # Check connection
            logging.info("Connected to MongoDB!")
            return self.db  # Return the database object
        except ConnectionFailure as e:
            logging.error(f"Could not connect to MongoDB: {e}")
            raise  # Re-raise to stop execution if connection fails
        except Exception as e:
            logging.error(f"An unexpected error occurred during connection: {e}")
            raise

    def close(self):
        """Closes the MongoDB connection."""
        if self.client:
            self.client.close()
            logging.info("MongoDB connection closed.")

if os.getenv("MONGO_URI") is None or os.getenv("MONGO_DB_NAME") is None:
    raise ValueError("Environment variables MONGO_URI and MONGO_DB_NAME must be set")

db = Database(
    connection_string=os.getenv("MONGO_URI"),
    db_name=os.getenv("MONGO_DB_NAME")
)
