import os
import logging
from fastapi import Depends, HTTPException, status, Request
from jose import jwt, JWTError
from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional

from src.api.utils.account import *
from src.service import oauth2_scheme
from ...service.database import users_collection, roles_collection, permissions_collection, role_has_permission_collection
from ..types.api import User, UserInDB
from ...service.database import setup_database

# --- Dependency functions ---
async def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    try:
        user_doc = await users_collection.find_one({"username": username})
        if not user_doc:
            logging.warning(f"Authentication failed: User '{username}' not found.")
            return None
        
        if not verify_password(password, user_doc.get("password", "")): # Access 'password' field directly
            logging.warning(f"Authentication failed: Incorrect password for user '{username}'.")
            return None
        
        return UserInDB(**user_doc) # Return as UserInDB Pydantic model
    except Exception as e:
        logging.error(f"Error during user authentication for '{username}': {e}", exc_info=True)
        return None

async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # First try to get token from cookie
        token_from_cookie = request.cookies.get("access_token")
        if token_from_cookie and token_from_cookie.startswith("Bearer "):
            token = token_from_cookie[7:]  # Remove "Bearer " prefix
        
        if not token:
            logging.warning("No token found in either cookie or authorization header")
            raise credentials_exception
        
        try:
            # Verify and decode the JWT token
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
            username: Optional[str] = payload.get("sub")
            user_id: Optional[str] = payload.get("user_id")
            
            if username is None or user_id is None:
                logging.warning("JWT payload missing required claims (sub or user_id)")
                raise credentials_exception
            
        except JWTError as e:
            logging.warning(f"JWT decode error: {str(e)}")
            raise credentials_exception
        
        # Fetch user from database
        user_doc = await users_collection.aggregate([
            {
                "$match": {
                    "user_id": user_id,
                    "username": username
                }
            },
            {
                "$lookup": {
                    "from": "roles",
                    "localField": "role_id",
                    "foreignField": "role_id",
                    "as": "role"
                }
            },
            {
                "$unwind": "$role"
            },
            {
                "$project": {
                    "user_id": 1,
                    "username": 1,
                    "role_id": 1,
                    "role_name": "$role.role_name",
                    "organization_id": 1,
                    "name": 1,
                    "email": 1,
                    "is_active": 1,
                    "is_primary_admin": 1,
                    "tokens_allowed": 1,
                    "created_at": 1,
                    "updated_at": 1
                }
            }
        ]).to_list(length=1)
        if user_doc:
            user_doc = user_doc[0]
        # user_doc = await users_collection.find_one({"user_id": user_id, "username": username})
        
        if user_doc is None:
            logging.warning(f"User '{username}' (ID: {user_id}) from token not found in database")
            raise credentials_exception
        
        return User(**user_doc)
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Unexpected error during token validation: {str(e)}", exc_info=True)
        raise credentials_exception

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

async def get_role_name_by_id(role_id: str) -> Optional[str]:
    role_doc = await roles_collection.find_one({"role_id": role_id})
    return role_doc.get("role_name") if role_doc else None

async def verify_role(user: User, role_name: str) -> bool:
    try:
        user_role_name = await get_role_name_by_id(user.role_id)
        return user_role_name == role_name
    except Exception as e:
        logging.error(f"Role verification error for user {user.username}, role {role_name}: {e}", exc_info=True)
        return False

async def check_permission(user: User, permission_name: str) -> bool:
    try:
        user_role_id = user.role_id
        if not user_role_id:
            return False

        user_role_name = await get_role_name_by_id(user_role_id)
        if user_role_name == "superadmin": # Superadmin has all permissions
            return True
        
        permission = await permissions_collection.find_one({"permission_name": permission_name})
        if not permission:
            logging.warning(f"Permission '{permission_name}' not found in database.")
            return False
        
        permission_id = permission.get("permission_id")
        has_permission = await role_has_permission_collection.find_one({
            "role_id": user_role_id,
            "permission_id": permission_id
        })
        return bool(has_permission)
    except Exception as e:
        logging.error(f"Permission check error for user {user.username}, permission {permission_name}: {e}", exc_info=True)
        return False

async def check_email_exists(email: str, exclude_user_id: Optional[str] = None) -> bool:
    query = {"email": email}
    if exclude_user_id:
        query["user_id"] = {"$ne": exclude_user_id}
    return await users_collection.find_one(query) is not None

async def check_username_exists(username: str, exclude_user_id: Optional[str] = None) -> bool:
    query = {"username": username}
    if exclude_user_id:
        query["user_id"] = {"$ne": exclude_user_id}
    return await users_collection.find_one(query) is not None

async def seed_initial_data():
    logging.info("Seeding initial data if not exists...")
    # Roles
    current_time = datetime.now(timezone.utc)
    roles_to_seed = [
        {
            "role_id": str(uuid4()),
            "role_name": "superadmin",
            "description": "Super Administrator",
            "created_at": current_time,
            "updated_at": current_time
        },
        {
            "role_id": str(uuid4()),
            "role_name": "admin",
            "description": "Administrator",
            "created_at": current_time,
            "updated_at": current_time
        },
        {
            "role_id": str(uuid4()),
            "role_name": "user",
            "description": "Standard User",
            "created_at": current_time,
            "updated_at": current_time
        }
    ]
    for role_data in roles_to_seed:
        if not await roles_collection.find_one({"role_name": role_data["role_name"]}):
            await roles_collection.insert_one(role_data)
            logging.info(f"Seeded role: {role_data['role_name']}")

    # Permissions
    permissions_to_seed = [
        {
            "permission_id": str(uuid4()),
            "permission_name": "create_user",
            "description": "Can create users",
            "created_at": current_time,
            "updated_at": current_time
        },
        {
            "permission_id": str(uuid4()),
            "permission_name": "create_admin",
            "description": "Can create admins",
            "created_at": current_time,
            "updated_at": current_time
        },
        {
            "permission_id": str(uuid4()),
            "permission_name": "manage_organization",
            "description": "Can manage organization settings",
            "created_at": current_time,
            "updated_at": current_time
        },
        {
            "permission_id": str(uuid4()),
            "permission_name": "view_all_organizations",
            "description": "Can view all organizations (Superadmin level)",
            "created_at": current_time,
            "updated_at": current_time
        },
        {
            "permission_id": str(uuid4()),
            "permission_name": "distribute_tokens",
            "description": "Can distribute organization tokens to users",
            "created_at": current_time,
            "updated_at": current_time
        }
        # Add more permissions as needed
    ]
    for perm_data in permissions_to_seed:
        if not await permissions_collection.find_one({"permission_name": perm_data["permission_name"]}):
            await permissions_collection.insert_one(perm_data)
            logging.info(f"Seeded permission: {perm_data['permission_name']}")

    # Role-Permission Mappings for Admin Role
    admin_role = await roles_collection.find_one({"role_name": "admin"})
    if admin_role:
        admin_role_id = admin_role["role_id"]
        permissions_for_admin = ["create_user", "create_admin", "manage_organization", "distribute_tokens"]
        for perm_name in permissions_for_admin:
            permission = await permissions_collection.find_one({"permission_name": perm_name})
            if permission:
                permission_id = permission["permission_id"]
                if not await role_has_permission_collection.find_one({"role_id": admin_role_id, "permission_id": permission_id}):
                    await role_has_permission_collection.insert_one({
                        "role_id": admin_role_id,
                        "permission_id": permission_id,
                        "assigned_at": current_time,
                        "created_at": current_time,
                        "updated_at": current_time
                    })
                    logging.info(f"Assigned permission '{perm_name}' to role 'admin'")
    
    # Create default Superadmin if none exists
    superadmin_role = await roles_collection.find_one({"role_name": "superadmin"})
    if superadmin_role and not await users_collection.find_one({"role_id": superadmin_role["role_id"]}):
        default_superadmin_username = os.getenv("DEFAULT_SUPERADMIN_USERNAME", "superadmin")
        default_superadmin_password = os.getenv("DEFAULT_SUPERADMIN_PASSWORD", "SuperStrongP@ssw0rd!") # CHANGE THIS IN PRODUCTION!
        default_superadmin_email = os.getenv("DEFAULT_SUPERADMIN_EMAIL", "superadmin@example.com")

        if await check_username_exists(default_superadmin_username) or await check_email_exists(default_superadmin_email):
            logging.warning(f"Default superadmin username '{default_superadmin_username}' or email '{default_superadmin_email}' already exists. Skipping creation.")
        else:
            superadmin_user_data = {
                "user_id": str(uuid4()),
                "role_id": superadmin_role["role_id"],
                "organization_id": "GLOBAL_SUPERADMIN_ORG", # Superadmins might not belong to a regular org
                "name": "Super Admin",
                "username": default_superadmin_username,
                "email": default_superadmin_email,
                "password": get_password_hash(default_superadmin_password), # Storing hashed password under 'password' key
                "is_active": True,
                "is_primary_admin": True, # Superadmins are considered primary
                "tokens_allowed": 0,
                "created_at": current_time,
                "updated_at": current_time,
            }
            await users_collection.insert_one(superadmin_user_data)
            logging.info(f"Created default superadmin: {default_superadmin_username} with password: {default_superadmin_password} (Ensure to change this password!)")

    logging.info("Initial data seeding complete.")
