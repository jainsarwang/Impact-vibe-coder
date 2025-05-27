from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.security import verify_token
from app.schema.user_models import TokenData
from app.db.db import get_database
from typing import Optional
import uuid

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    token_data = TokenData(
        user_id=user_id,
        role_id=payload.get("role_id"),
        organization_id=payload.get("organization_id")
    )
    
    # Verify user exists and is active
    db = await get_database()
    user = await db.users.find_one({"user_id": user_id, "is_active": True})
    if user is None:
        raise credentials_exception
    
    return user

async def require_permission(permission_name: str):
    """Decorator to require specific permission"""
    async def permission_checker(current_user = Depends(get_current_user)):
        db = await get_database()
        
        # Get user's role permissions
        role_permissions = await db.role_has_permissions.find({
            "role_id": current_user["role_id"]
        }).to_list(length=None)
        
        permission_ids = [rp["permission_id"] for rp in role_permissions]
        
        # Check if user has the required permission
        permission = await db.permissions.find_one({
            "permission_id": {"$in": permission_ids},
            "permission_name": permission_name
        })
        
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission_name}' required"
            )
        
        return current_user
    
    return permission_checker

def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())