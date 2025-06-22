from typing import Optional, Union, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

# --- Project Generation Request ---
class ProjectGenerationRequest(BaseModel):
    class ContentItem(BaseModel):
        type: str = Field(..., description="The type of content (text, image, etc.)")
        text: Optional[str] = Field(None, description="The text content if type is 'text'")
        image_url: Optional[str] = Field(
            None, description="The image URL if type is 'image'"
        )

    class ChatMessage(BaseModel):
        role: str = Field(
            ..., description="The role of the message sender (user or assistant)"
        )
        content: Union[str, List["ProjectGenerationRequest.ContentItem"]] = Field(
            ...,
            description="The content of the message, either a string or a list of content items",
        )

    messages: List[ChatMessage] = Field(..., description="The conversation history")
    debug: Optional[bool] = Field(False, description="Whether to enable debug logging")
    deep_thinking_mode: Optional[bool] = Field(
        False, description="Whether to enable deep thinking mode"
    )
    search_before_planning: Optional[bool] = Field(
        False, description="Whether to search before planning"
    )


# --- Base Models ---
class UserBase(BaseModel):
    """Base model for user data"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)

# --- Request Models ---
class AdminCreateRequest(BaseModel):
    """Request model for superadmin to create a new admin + org"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    organization_name: str = Field(..., min_length=1, max_length=100)
    total_tokens: int = Field(..., ge=0)

class UserCreateRequest(BaseModel):
    """Request model for admin to create a user or another admin"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    tokens: int = 0

class OrganizationCreate(BaseModel):
    """Request model for creating a new organization"""
    organization_name: str = Field(..., min_length=1, max_length=100)
    total_tokens: int = Field(..., ge=0)

class ProjectCreate(BaseModel):
    """Request model for creating a new project"""
    project_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class ChatMessage(BaseModel):
    """Request model for sending a chat message"""
    message: str = Field(..., min_length=1)

# --- Response Models ---
class Token(BaseModel):
    """Response model for authentication token"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Model for JWT payload data"""
    sub: str  # username
    user_id: str
    role_id: Optional[str] = None
    organization_id: Optional[str] = None
    is_primary_admin: bool = False

class User(UserBase):
    """Response model for user data"""
    user_id: str
    role_id: str
    role_name: Optional[str] = None
    organization_id: str
    is_active: bool
    is_primary_admin: bool = False
    created_at: datetime
    updated_at: datetime
    tokens: int = 0  # Individual user token balance

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class UserInDB(User):
    """Internal model for user data with hashed password"""
    password: str  # Hashed password string from DB

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class Organization(OrganizationCreate):
    """Response model for organization data"""
    organization_id: str
    tokens_remaining: int
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class AdminCreateResponse(BaseModel):
    """Response model for admin creation"""
    username: str
    password: str  # Plain text password, to be shown once
    organization_id: str
    user_id: str

class UserCreateResponse(BaseModel):
    """Response model for user creation"""
    username: str
    password: str  # Plain text password, to be shown once
    user_id: str

class Project(ProjectCreate):
    """Response model for project data"""
    project_id: str
    user_id: str
    organization_id: str
    is_deployed: bool
    tokens_consumed: int
    created_at: datetime
    updated_at: datetime
    project_link: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class ChatMessageOut(ChatMessage):
    """Response model for chat messages"""
    chat_history_id: str
    chat_id: str
    user_id: str
    direction: str  # e.g., "outgoing", "incoming"
    tokens_used: int
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class UpdateToken(BaseModel) :
    tokens: int

# Email Credential Response
class EmailCredentialResponse(BaseModel):
    class EmailCredential(BaseModel): # For response
        id: str # mongoDB id
        email: str
        host: str
        port: int
        password: str
        user_id: str
        created_at: datetime
        updated_at: datetime

    data: Optional[EmailCredential]