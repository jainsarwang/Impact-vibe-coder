
from typing import Optional

from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    status: bool


class Task(TaskBase):
    id: int
    status: bool

    class Config:
        orm_mode = True
