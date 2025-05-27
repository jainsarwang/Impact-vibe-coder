import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel
import uuid
from typing import Dict, List

# Database connection setup
async def get_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    return client["impact_vibe_coder"]

# Sample data generators
def generate_sample_data():
    # Organizations
    organizations = [
        {
            "organization_id": str(uuid.uuid4()),
            "organization_name": "TechCorp",
            "total_tokens": 1000000,
            "tokens_remaining": 750000,
            "credit_reset_date": datetime.now() + timedelta(days=30),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "organization_id": str(uuid.uuid4()),
            "organization_name": "DataSystems",
            "total_tokens": 500000,
            "tokens_remaining": 350000,
            "credit_reset_date": datetime.now() + timedelta(days=30),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]

    # Roles
    roles = [
        {
            "role_id": str(uuid.uuid4()),
            "role_name": "superadmin",
            "description": "System super administrator with all privileges",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "role_id": str(uuid.uuid4()),
            "role_name": "admin",
            "description": "Organization administrator",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "role_id": str(uuid.uuid4()),
            "role_name": "user",
            "description": "Regular organization user",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]

    # Permissions
    permissions = [
        {
            "permission_id": str(uuid.uuid4()),
            "permission_name": "create_organization",
            "description": "Can create new organizations",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "permission_id": str(uuid.uuid4()),
            "permission_name": "create_admin",
            "description": "Can create admin users",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "permission_id": str(uuid.uuid4()),
            "permission_name": "create_user",
            "description": "Can create regular users",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "permission_id": str(uuid.uuid4()),
            "permission_name": "manage_tokens",
            "description": "Can manage token allocations",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "permission_id": str(uuid.uuid4()),
            "permission_name": "view_all_projects",
            "description": "Can view all projects in organization",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]

    # Role-Permission mappings
    role_has_permission = [
        # Superadmin gets all permissions
        {
            "role_id": next(r["role_id"] for r in roles if r["role_name"] == "superadmin"),
            "permission_id": next(p["permission_id"] for p in permissions if p["permission_name"] == "create_organization"),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "role_id": next(r["role_id"] for r in roles if r["role_name"] == "superadmin"),
            "permission_id": next(p["permission_id"] for p in permissions if p["permission_name"] == "create_admin"),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        # Admin gets specific permissions
        {
            "role_id": next(r["role_id"] for r in roles if r["role_name"] == "admin"),
            "permission_id": next(p["permission_id"] for p in permissions if p["permission_name"] == "create_user"),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "role_id": next(r["role_id"] for r in roles if r["role_name"] == "admin"),
            "permission_id": next(p["permission_id"] for p in permissions if p["permission_name"] == "view_all_projects"),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]

    # Users (with hashed passwords - "password123" for all sample users)
    users = [
        # Superadmin
        {
            "user_id": str(uuid.uuid4()),
            "role_id": next(r["role_id"] for r in roles if r["role_name"] == "superadmin"),
            "organization_id": None,  # Superadmin isn't tied to a specific org
            "name": "Super Admin",
            "username": "superadmin",
            "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password123
            "email": "superadmin@example.com",
            "is_active": True,
            "last_login": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        # TechCorp Admin
        {
            "user_id": str(uuid.uuid4()),
            "role_id": next(r["role_id"] for r in roles if r["role_name"] == "admin"),
            "organization_id": organizations[0]["organization_id"],
            "name": "TechCorp Admin",
            "username": "techcorp_admin",
            "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password123
            "email": "admin@techcorp.com",
            "is_active": True,
            "last_login": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        # DataSystems Admin
        {
            "user_id": str(uuid.uuid4()),
            "role_id": next(r["role_id"] for r in roles if r["role_name"] == "admin"),
            "organization_id": organizations[1]["organization_id"],
            "name": "DataSystems Admin",
            "username": "datasystems_admin",
            "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password123
            "email": "admin@datasystems.com",
            "is_active": True,
            "last_login": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        # Regular users
        {
            "user_id": str(uuid.uuid4()),
            "role_id": next(r["role_id"] for r in roles if r["role_name"] == "user"),
            "organization_id": organizations[0]["organization_id"],
            "name": "John Developer",
            "username": "john.dev",
            "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password123
            "email": "john.dev@techcorp.com",
            "is_active": True,
            "last_login": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "user_id": str(uuid.uuid4()),
            "role_id": next(r["role_id"] for r in roles if r["role_name"] == "user"),
            "organization_id": organizations[1]["organization_id"],
            "name": "Jane Analyst",
            "username": "jane.analyst",
            "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password123
            "email": "jane.analyst@datasystems.com",
            "is_active": True,
            "last_login": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]

    # Credit Allocations
    credit_allocations = [
        {
            "role_id": next(r["role_id"] for r in roles if r["role_name"] == "admin"),
            "organization_id": organizations[0]["organization_id"],
            "tokens_allowed": 100000,
            "tokens_used": 25000,
            "is_active": True,
            "reset_period": datetime.now() + timedelta(days=30),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "role_id": next(r["role_id"] for r in roles if r["role_name"] == "user"),
            "organization_id": organizations[0]["organization_id"],
            "tokens_allowed": 50000,
            "tokens_used": 10000,
            "is_active": True,
            "reset_period": datetime.now() + timedelta(days=30),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "role_id": next(r["role_id"] for r in roles if r["role_name"] == "admin"),
            "organization_id": organizations[1]["organization_id"],
            "tokens_allowed": 50000,
            "tokens_used": 15000,
            "is_active": True,
            "reset_period": datetime.now() + timedelta(days=30),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "role_id": next(r["role_id"] for r in roles if r["role_name"] == "user"),
            "organization_id": organizations[1]["organization_id"],
            "tokens_allowed": 25000,
            "tokens_used": 5000,
            "is_active": True,
            "reset_period": datetime.now() + timedelta(days=30),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]

    # Projects
    projects = [
        {
            "project_id": str(uuid.uuid4()),
            "user_id": users[3]["user_id"],  # John Developer
            "organization_id": organizations[0]["organization_id"],
            "project_name": "E-commerce Platform",
            "description": "Next-gen online shopping platform",
            "is_deployed": True,
            "project_directory_link": "https://storage.example.com/projects/123",
            "project_link": "https://shop.techcorp.com",
            "tokens_consumed": 15000,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "project_id": str(uuid.uuid4()),
            "user_id": users[4]["user_id"],  # Jane Analyst
            "organization_id": organizations[1]["organization_id"],
            "project_name": "Data Analytics Dashboard",
            "description": "Real-time business intelligence dashboard",
            "is_deployed": False,
            "project_directory_link": "https://storage.example.com/projects/456",
            "tokens_consumed": 8000,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]

    # Chats
    chats = [
        {
            "chat_id": str(uuid.uuid4()),
            "project_id": projects[0]["project_id"],
            "user_id": users[3]["user_id"],
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "chat_id": str(uuid.uuid4()),
            "project_id": projects[1]["project_id"],
            "user_id": users[4]["user_id"],
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]

    # Chat History
    chat_history = [
        {
            "chat_history_id": str(uuid.uuid4()),
            "chat_id": chats[0]["chat_id"],
            "user_id": users[3]["user_id"],
            "message": "How can I optimize the checkout flow?",
            "direction": "outbound",
            "tokens_used": 15,
            "created_at": datetime.now()
        },
        {
            "chat_history_id": str(uuid.uuid4()),
            "chat_id": chats[0]["chat_id"],
            "user_id": users[3]["user_id"],
            "message": "Here are some suggestions for optimizing the checkout flow...",
            "direction": "inbound",
            "tokens_used": 42,
            "created_at": datetime.now()
        },
        {
            "chat_history_id": str(uuid.uuid4()),
            "chat_id": chats[1]["chat_id"],
            "user_id": users[4]["user_id"],
            "message": "What's the best way to visualize monthly sales data?",
            "direction": "outbound",
            "tokens_used": 18,
            "created_at": datetime.now()
        }
    ]

    return {
        "organizations": organizations,
        "roles": roles,
        "permissions": permissions,
        "role_has_permission": role_has_permission,
        "users": users,
        "credit_allocations": credit_allocations,
        "projects": projects,
        "chats": chats,
        "chat_history": chat_history
    }

# Function to create indexes
async def create_indexes(db):
    # Organization indexes
    await db.organizations.create_indexes([
        IndexModel([("organization_id", 1)], unique=True),
        IndexModel([("organization_name", 1)], unique=True)
    ])
    
    # User indexes
    await db.users.create_indexes([
        IndexModel([("user_id", 1)], unique=True),
        IndexModel([("username", 1)], unique=True),
        IndexModel([("email", 1)], unique=True),
        IndexModel([("organization_id", 1)]),
        IndexModel([("role_id", 1)])
    ])
    
    # Role indexes
    await db.roles.create_indexes([
        IndexModel([("role_id", 1)], unique=True),
        IndexModel([("role_name", 1)], unique=True)
    ])
    
    # Project indexes
    await db.projects.create_indexes([
        IndexModel([("project_id", 1)], unique=True),
        IndexModel([("user_id", 1)]),
        IndexModel([("organization_id", 1)])
    ])
    
    # Add more indexes as needed for other collections

# Function to insert sample data
async def insert_sample_data(db):
    sample_data = generate_sample_data()
    
    # Insert data in proper order to maintain referential integrity
    await db.organizations.insert_many(sample_data["organizations"])
    await db.roles.insert_many(sample_data["roles"])
    await db.permissions.insert_many(sample_data["permissions"])
    await db.role_has_permission.insert_many(sample_data["role_has_permission"])
    await db.users.insert_many(sample_data["users"])
    await db.credit_allocations.insert_many(sample_data["credit_allocations"])
    await db.projects.insert_many(sample_data["projects"])
    await db.chats.insert_many(sample_data["chats"])
    await db.chat_history.insert_many(sample_data["chat_history"])
    
    print("Successfully inserted all sample data!")

# Main function
async def main():
    db = await get_db()
    
    # Clear existing collections (optional - be careful in production!)
    # await db.organizations.delete_many({})
    # await db.roles.delete_many({})
    # ... and so on for other collections
    
    # Create indexes
    await create_indexes(db)
    
    # Insert sample data
    await insert_sample_data(db)

if __name__ == "__main__":
    asyncio.run(main())