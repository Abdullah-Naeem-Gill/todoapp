from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session,select
from models import Task
from database import get_db
from pydantic import BaseModel, constr
from typing import List, Optional

router = APIRouter()
class TaskResponse(BaseModel):
    msg: str
    task_id: Optional[int] = None

class TaskCreate(BaseModel):
    title: constr(min_length=1, max_length=100) 
    description: Optional[constr(max_length=500)] = None

class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str]


@router.post("/", tags=["Task Management"])
async def create_task(title: str, description: str, db: Session = Depends(get_db)):
    new_task = Task(title=title, description=description)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return {"msg": "Task created", "task_id": new_task.id}

@router.get("/", response_model=List[TaskRead], tags=["Task Management"])
async def get_all_tasks(db: Session = Depends(get_db)):
    tasks = await db.exec(select(Task))
    return tasks.all()

@router.get("/{task_id}", response_model=TaskRead, tags=["Task Management"])
async def get_task_by_id(task_id: int, db: Session = Depends(get_db)):
    task = await db.exec(select(Task).where(Task.id == task_id))
    task = task.first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@router.put("/{task_id}", tags=["Task Management"])
async def update_task(task_id: int, title: str, description: str, db: Session = Depends(get_db)):
    task = await db.exec(select(Task).where(Task.id == task_id))
    task = task.first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.title = title
    task.description = description
    await db.commit()
    return {"msg": "Task updated"}

@router.delete("/{task_id}", tags=["Task Management"])
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = await db.exec(select(Task).where(Task.id == task_id))
    task = task.first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await db.delete(task)
    await db.commit()
    return {"msg": "Task deleted"}
