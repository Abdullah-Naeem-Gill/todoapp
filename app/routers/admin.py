from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from models import User, Task, TaskAssignment
from database import get_db
from auth import get_current_user

router = APIRouter()

@router.post("/assign-task", tags=["Admin"])
async def assign_task(task_id: int, user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    task = await db.execute(select(Task).where(Task.id == task_id))
    user = await db.execute(select(User).where(User.id == user_id))
    
    task = task.scalar_one_or_none()
    user = user.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    task_assignment = TaskAssignment(user_id=user_id, task_id=task_id)
    db.add(task_assignment)
    await db.commit()
    await db.refresh(task_assignment)

    return {"msg": "Task assigned successfully", "task_assignment_id": task_assignment.id}

@router.delete("/unassign-task/{task_id}/{user_id}", tags=["Admin"])
async def unassign_task(task_id: int, user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    assignment = await db.execute(select(TaskAssignment).where(TaskAssignment.task_id == task_id, TaskAssignment.user_id == user_id))
    assignment = assignment.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Task not assigned to this user.")
    
    await db.delete(assignment)
    await db.commit()
    return {"msg": "Task unassigned successfully"}
