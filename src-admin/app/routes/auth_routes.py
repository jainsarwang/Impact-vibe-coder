from fastapi import APIRouter, Depends, HTTPException, status
from app.schema.user_models import UserCreate, UserLogin, Token, PasswordReset
from app.controller.auth_controller import AuthController
from app.utils.auth_utils import get_current_user

auth_router = APIRouter()
auth_controller = AuthController()

@auth_router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    return await auth_controller.register_user(user_data)

@auth_router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """Login user and return access token"""
    return await auth_controller.login_user(login_data)

@auth_router.post("/change-password")
async def change_password(
    password_data: PasswordReset,
    current_user = Depends(get_current_user)
):
    """Change user password"""
    return await auth_controller.change_password(current_user["user_id"], password_data)

@auth_router.get("/me", response_model=dict)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    # Remove password from response
    user_info = {k: v for k, v in current_user.items() if k != "password"}
    return {"user": user_info}

@auth_router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    """Logout user (client should remove token)"""
    return {"message": "Logged out successfully"}