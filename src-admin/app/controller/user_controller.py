from fastapi import HTTPException, status
from app.schema.user_models import UserUpdate, UserResponse
from app.db.db import get_database
from datetime import datetime
from typing import List, Optional

class UserController:
    
    async def get_user_profile(self, user_id: str) -> UserResponse:
        """Get user profile"""
        db = await get_database()
        
        user = await db.users.find_one({"user_id": user_id}, {"password": 0})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(**user)
    
    async def update_user_profile(self, user_id: str, update_data: UserUpdate) -> UserResponse:
        """Update user profile"""
        db = await get_database()
        
        # Check if user exists
        user = await db.users.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prepare update data
        update_fields = {}
        if update_data.name is not None:
            update_fields["name"] = update_data.name
        if update_data.email is not None:
            # Check if email is already taken by another user
            existing_email = await db.users.find_one({
                "email": update_data.email,
                "user_id": {"$ne": user_id}
            })
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            update_fields["email"] = update_data.email
        if update_data.role_id is not None:
            # Verify role exists
            role = await db.roles.find_one({"role_id": update_data.role_id})
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid role ID"
                )
            update_fields["role_id"] = update_data.role_id
        if update_data.is_active is not None:
            update_fields["is_active"] = update_data.is_active
        
        update_fields["updated_at"] = datetime.utcnow()
        
        # Update user
        result = await db.users.update_one(
            {"user_id": user_id},
            {"$set": update_fields}
        )
        
        if result.modified_count:
            updated_user = await db.users.find_one({"user_id": user_id}, {"password": 0})
            return UserResponse(**updated_user)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )
    
    async def get_users_by_organization(self, organization_id: str, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Get users in an organization"""
        db = await get_database()
        
        users = await db.users.find(
            {"organization_id": organization_id},
            {"password": 0}
        ).skip(skip).limit(limit).to_list(length=None)
        
        return [UserResponse(**user) for user in users]
    
    async def deactivate_user(self, user_id: str) -> dict:
        """Deactivate a user account"""
        db = await get_database()
        
        result = await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count:
            return {"message": "User deactivated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )