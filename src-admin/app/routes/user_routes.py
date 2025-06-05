from fastapi import APIRouter, Depends, Query
from app.schema.user_models import UserUpdate, UserResponse
from app.controller.user_controller import UserController
from app.utils.auth_utils import get_current_user, require_permission
from typing import List

user_router = APIRouter()
user_controller = UserController()

@user_router.get("/profile", response_model=UserResponse)
async def get_profile(current_user = Depends(get_current_user)):
    """Get current user profile"""
    return await user_controller.get_user_profile(current_user["user_id"])

@user_router.put("/profile", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user = Depends(get_current_user)
):
    """Update current user profile"""
    return await user_controller.update_user_profile(current_user["user_id"], update_data)

@user_router.get("/organization/{organization_id}", response_model=List[UserResponse])
async def get_organization_users(
    organization_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user = Depends(require_permission("view_users"))
):
    """Get users in an organization (requires view_users permission)"""
    return await user_controller.get_users_by_organization(organization_id, skip, limit)

@user_router.patch("/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user = Depends(require_permission("manage_users"))
):
    """Deactivate a user account (requires manage_users permission)"""
    return await user_controller.deactivate_user(user_id)

@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user = Depends(require_permission("view_users"))
):
    """Get user by ID (requires view_users permission)"""
    return await user_controller.get_user_profile(user_id)
