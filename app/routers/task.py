from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from models import Task
from database import get_db
from pydantic import BaseModel, constr
from typing import List, Optional
from auth import get_current_user
from models import User

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

@router.post("/", response_model=TaskResponse, tags=["Task Management"])
async def create_task(task_create: TaskCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    new_task = Task(**task_create.dict())
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return {"msg": "Task created", "task_id": new_task.id}

@router.get("/", response_model=List[TaskRead], tags=["Task Management"])
async def get_all_tasks(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tasks = await db.execute(select(Task))
    return tasks.scalars().all()

@router.get("/{task_id}", response_model=TaskRead, tags=["Task Management"])
async def get_task_by_id(task_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    task = await db.execute(select(Task).where(Task.id == task_id))
    task = task.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@router.put("/{task_id}", tags=["Task Management"])
async def update_task(task_id: int, task_create: TaskCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    task = await db.execute(select(Task).where(Task.id == task_id))
    task = task.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.title = task_create.title
    task.description = task_create.description
    await db.commit()
    return {"msg": "Task updated"}

@router.delete("/{task_id}", tags=["Task Management"])
async def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    task = await db.execute(select(Task).where(Task.id == task_id))
    task = task.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await db.delete(task)
    await db.commit()
    return {"msg": "Task deleted"}
