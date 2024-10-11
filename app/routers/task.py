from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session,select
from models import Task
from database import get_db

router = APIRouter()

@router.post("/", tags=["Task Management"])
async def create_task(title: str, description: str, db: Session = Depends(get_db)):
    new_task = Task(title=title, description=description)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return {"msg": "Task created", "task_id": new_task.id}

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
