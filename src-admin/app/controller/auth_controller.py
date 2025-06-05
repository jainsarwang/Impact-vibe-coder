from fastapi import HTTPException, status
from app.schema.user_models import UserCreate, UserLogin, Token, PasswordReset
from app.utils.security import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.utils.auth_utils import generate_id
from app.db.db import get_database
from datetime import datetime, timedelta

class AuthController:
    
    async def register_user(self, user_data: UserCreate) -> dict:
        """Register a new user"""
        db = await get_database()
        
        # Check if username or email already exists
        existing_user = await db.users.find_one({
            "$or": [
                {"username": user_data.username},
                {"email": user_data.email}
            ]
        })
        
        if existing_user:
            if existing_user["username"] == user_data.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Verify role and organization exist
        role = await db.roles.find_one({"role_id": user_data.role_id})
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role ID"
            )
        
        organization = await db.organizations.find_one({"organization_id": user_data.organization_id})
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid organization ID"
            )
        
        # Create user
        user_id = generate_id()
        hashed_password = get_password_hash(user_data.password)
        
        new_user = {
            "user_id": user_id,
            "role_id": user_data.role_id,
            "organization_id": user_data.organization_id,
            "name": user_data.name,
            "username": user_data.username,
            "email": user_data.email,
            "password": hashed_password,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.users.insert_one(new_user)
        
        if result.inserted_id:
            # Remove password from response
            new_user.pop("password")
            return {"message": "User registered successfully", "user": new_user}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register user"
            )
    
    async def login_user(self, login_data: UserLogin) -> Token:
        """Authenticate user and return token"""
        db = await get_database()
        
        # Find user by username
        user = await db.users.find_one({"username": login_data.username})
        
        if not user or not verify_password(login_data.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive"
            )
        
        # Update last login
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"last_login": datetime.utcnow(), "updated_at": datetime.utcnow()}}
        )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user["user_id"],
                "role_id": user["role_id"],
                "organization_id": user["organization_id"]
            },
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user["user_id"],
            role_id=user["role_id"],
            organization_id=user["organization_id"]
        )
    
    async def change_password(self, user_id: str, password_data: PasswordReset) -> dict:
        """Change user password"""
        db = await get_database()
        
        # Get current user
        user = await db.users.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(password_data.current_password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        new_hashed_password = get_password_hash(password_data.new_password)
        result = await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"password": new_hashed_password, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count:
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to change password"
            )
