from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role_id: str
    organization_id: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    role_id: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    user_id: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class UserLogin(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: str
    role_id: str
    organization_id: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role_id: Optional[str] = None
    organization_id: Optional[str] = None

class PasswordReset(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)