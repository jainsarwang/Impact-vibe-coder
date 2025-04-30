from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class TodoCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    due_date: Optional[date] = None
    priority: Optional[str] = Field(None, description="Priority level (e.g., High, Medium, Low)")

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    due_date: Optional[date] = None
    priority: Optional[str] = Field(None, description="Priority level (e.g., High, Medium, Low)")
    completed: Optional[bool] = None

class Todo(TodoCreate):
    id: int

    class Config:
        orm_mode = True
