from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import PriorityEnum, TaskStatusEnum
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from app.services import task_service
from app.config import settings

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskOut])
def get_tasks(
    status: Optional[TaskStatusEnum] = None,
    priority: Optional[PriorityEnum] = None,
    overdue_only: bool = False,
    sort_by: str = "priority",
    db: Session = Depends(get_db),
):
    return task_service.list_tasks(
        db, settings.DEMO_USER_ID, status=status, priority=priority,
        overdue_only=overdue_only, sort_by=sort_by,
    )


@router.post("", response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    return task_service.create_task(db, settings.DEMO_USER_ID, payload)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = task_service.get_task(db, settings.DEMO_USER_ID, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = task_service.update_task(db, settings.DEMO_USER_ID, task_id, payload)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/complete", response_model=TaskOut)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = task_service.complete_task(db, settings.DEMO_USER_ID, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    deleted = task_service.delete_task(db, settings.DEMO_USER_ID, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
