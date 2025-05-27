from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import os
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def get_database():
    return db.database

async def init_db():
    """Initialize database connection and create collections with schemas"""
    db_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DATABASE_NAME", "auth_system")
    
    db.client = AsyncIOMotorClient(db_url, server_api=ServerApi('1'))
    db.database = db.client[db_name]
    
    # Create collections with validation schemas
    from app.models.model import organization_schema,role_has_permission_schema,roles_schema,credit_allocation_schema,chats_history_schema,users_schema,permissions_flags_schema,permissions_schema,projects_schema,chats_schema

    collections_schemas = {
        "organizations": organization_schema,
        "roles": roles_schema,
        "credit_allocations": credit_allocation_schema,
        "users": users_schema,
        "role_has_permissions": role_has_permission_schema,
        "permissions": permissions_schema,
        "projects": projects_schema,
        "chats": chats_schema,
        "chats_history": chats_history_schema,
        "permissions_flags": permissions_flags_schema
    }
    
    for collection_name, schema in collections_schemas.items():
        try:
            await db.database.create_collection(collection_name, validator=schema)
        except Exception as e:
            # Collection might already exist
            pass
    
    # Create indexes
    await create_indexes()

async def create_indexes():
    """Create database indexes for better performance"""
    collections = db.database
    
    # Users collection indexes
    await collections.users.create_index("username", unique=True)
    await collections.users.create_index("email", unique=True)
    await collections.users.create_index("organization_id")
    await collections.users.create_index("role_id")
    
    # Organizations collection indexes
    await collections.organizations.create_index("organization_id", unique=True)
    
    # Roles collection indexes
    await collections.roles.create_index("role_id", unique=True)
    
    # Projects collection indexes
    await collections.projects.create_index("user_id")
    await collections.projects.create_index("organization_id")
    
    # Chats collection indexes
    await collections.chats.create_index("project_id")
    await collections.chats.create_index("user_id")

async def close_db():
    """Close database connection"""
    if db.client:
        db.client.close()