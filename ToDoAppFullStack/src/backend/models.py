from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: int = Field(3, ge=1, le=3)
    due_date: Optional[datetime] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    completed: bool

class Item(ItemBase):
    id: int
    owner_id: int
    created_date: datetime

    class Config:
        orm_mode = True
