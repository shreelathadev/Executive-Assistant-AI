#task_service.py
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

from app.db.models import Task, PriorityEnum, TaskStatusEnum
from app.schemas.task import TaskCreate, TaskUpdate

PRIORITY_ORDER = {
    PriorityEnum.critical: 0,
    PriorityEnum.high: 1,
    PriorityEnum.medium: 2,
    PriorityEnum.low: 3,
}


def create_task(db: Session, user_id: int, data: TaskCreate) -> Task:
    task = Task(user_id=user_id, **data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(
    db: Session,
    user_id: int,
    status: Optional[TaskStatusEnum] = None,
    priority: Optional[PriorityEnum] = None,
    overdue_only: bool = False,
    sort_by: str = "priority",
) -> list[Task]:
    query = db.query(Task).filter(Task.user_id == user_id)

    if status is not None:
        query = query.filter(Task.status == status)
    if priority is not None:
        query = query.filter(Task.priority == priority)
    if overdue_only:
        query = query.filter(Task.due_date < date.today(), Task.status != TaskStatusEnum.completed)

    tasks = query.all()

    if sort_by == "due_date":
        tasks.sort(key=lambda t: (t.due_date is None, t.due_date))
    else:  # default: priority
        tasks.sort(key=lambda t: PRIORITY_ORDER.get(t.priority, 99))

    return tasks


def get_task(db: Session, user_id: int, task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()


def update_task(db: Session, user_id: int, task_id: int, data: TaskUpdate) -> Optional[Task]:
    task = get_task(db, user_id, task_id)
    if not task:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def complete_task(db: Session, user_id: int, task_id: int) -> Optional[Task]:
    return update_task(db, user_id, task_id, TaskUpdate(status=TaskStatusEnum.completed))


def delete_task(db: Session, user_id: int, task_id: int) -> bool:
    task = get_task(db, user_id, task_id)
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True


def get_overdue_tasks(db: Session, user_id: int) -> list[Task]:
    return list_tasks(db, user_id, overdue_only=True)


def get_high_priority_open_tasks(db: Session, user_id: int) -> list[Task]:
    tasks = list_tasks(db, user_id)
    return [
        t for t in tasks
        if t.status != TaskStatusEnum.completed and t.priority in (PriorityEnum.critical, PriorityEnum.high)
    ]
