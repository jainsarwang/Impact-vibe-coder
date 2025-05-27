from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class OrganizationBase(BaseModel):
    organization_name: str = Field(..., min_length=1, max_length=100)
    total_tokens: int = Field(..., ge=0)
    tokens_remaining: int = Field(..., ge=0)

class OrganizationCreate(OrganizationBase):
    credit_reset_date: Optional[datetime] = None

class OrganizationUpdate(BaseModel):
    organization_name: Optional[str] = Field(None, min_length=1, max_length=100)
    total_tokens: Optional[int] = Field(None, ge=0)
    tokens_remaining: Optional[int] = Field(None, ge=0)
    credit_reset_date: Optional[datetime] = None

class OrganizationResponse(OrganizationBase):
    organization_id: str
    credit_reset_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime