import logging
import os
from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError, OperationFailure

from ..models.model import *

# Configure logging
logger = logging.getLogger(__name__)

if os.getenv("MONGO_URI") is None:
    raise ValueError("MONGO_URI is not set")

if os.getenv("MONGO_DB") is None:
    raise ValueError("MONGO_DB is not set")

try:
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    # Test the connection
    client.admin.command('ismaster')
except ServerSelectionTimeoutError:
    logger.error("Could not connect to MongoDB. Please check if MongoDB server is running.")
    raise
except PyMongoError as e:
    logger.error(f"MongoDB connection error: {e}")
    raise

db = client[os.getenv("MONGO_DB")]

# Initialize collections
organizations_collection = db["organizations"]
users_collection = db["users"]
roles_collection = db["roles"]
permissions_collection = db["permissions"]
role_has_permission_collection = db["role_has_permission"]
token_allocations_collection = db["token_allocations"]
projects_collection = db["projects"]
chats_collection = db["chats"]
chat_history_collection = db["chat_history"]
email_credential_collection = db["email_credential"]

async def setup_database():
    """Initialize database with collections and schemas"""
    logger.info("Setting up database...")

    try:
        # Test database connection
        await client.admin.command('ping')
        
        # Get list of existing collections
        existing_collections = await db.list_collection_names()
        
        # Create collections with validators if they don't exist
        collections_to_create = {
            "organizations": organization_schema,
            "users": users_schema,
            "roles": roles_schema,
            "permissions": permissions_schema,
            "role_has_permission": role_has_permission_schema,
            "token_allocations": token_allocation_schema,
            "projects": projects_schema,
            "chats": chats_schema,
            "chat_history": chats_history_schema,
            "permissions_flags": permissions_flags_schema,
            "email_credential": email_credential_schema
        }

        for coll_name, schema in collections_to_create.items():
            if coll_name not in existing_collections:
                logger.info(f"Creating {coll_name} collection...")
                try:
                    await db.create_collection(
                        coll_name,
                        validator=schema,
                        validationLevel="strict",
                        validationAction="error"
                    )
                    logger.info(f"Successfully created {coll_name} collection.")
                except OperationFailure as e:
                    if "already exists" in str(e):
                        logger.warning(f"Collection {coll_name} already exists. Skipping creation.")
                    else:
                        logger.error(f"Failed to create collection {coll_name}: {e}")
                        raise
                except PyMongoError as e:
                    logger.error(f"MongoDB error while creating collection {coll_name}: {e}")
                    raise

        logger.info("Database setup completed successfully.")
    except ServerSelectionTimeoutError as e:
        logger.error("Could not connect to MongoDB server during setup.")
        raise
    except PyMongoError as e:
        logger.error(f"MongoDB error during database setup: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during database setup: {e}")
        raise