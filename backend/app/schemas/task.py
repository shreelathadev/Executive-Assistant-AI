from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel
from app.db.models import PriorityEnum, TaskStatusEnum


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: PriorityEnum = PriorityEnum.medium
    status: TaskStatusEnum = TaskStatusEnum.todo
    due_date: Optional[date] = None
    project_id: Optional[int] = None
    notes: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[TaskStatusEnum] = None
    due_date: Optional[date] = None
    project_id: Optional[int] = None
    notes: Optional[str] = None


class TaskOut(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
