import os
from pymongo import MongoClient

if os.getenv("MONGO_URI") is None:
    raise ValueError("MONGO_URI is not set")

if os.getenv("MONGO_DB") is None:
    raise ValueError("MONGO_DB is not set")

client = MongoClient(os.getenv("MONGO_URI"))

db = client[os.getenv("MONGO_DB")]
