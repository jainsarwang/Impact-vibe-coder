from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RoleBase(BaseModel):
    role_name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=200)

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    role_name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, min_length=1, max_length=200)

class RoleResponse(RoleBase):
    role_id: str
    created_at: datetime
    updated_at: datetime
    permissions: Optional[List[str]] = []