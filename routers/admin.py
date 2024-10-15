from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_db
from models import User, Task, TaskAssignment

router = APIRouter()

@router.post("/assign-task", tags=["Admin"])
async def assign_task(task_id: int, user_id: int, db: Session = Depends(get_db)):
    task = await db.exec(select(Task).where(Task.id == task_id))
    user = await db.exec(select(User).where(User.id == user_id))
    
    task = task.first()
    user = user.first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    # Create TaskAssignment to assign the task to the user
    task_assignment = TaskAssignment(user_id=user_id, task_id=task_id)
    db.add(task_assignment)
    await db.commit()
    await db.refresh(task_assignment)

    return {"msg": "Task assigned successfully", "task_assignment_id": task_assignment.id}

@router.delete("/unassign-task/{task_id}/{user_id}", tags=["Admin"])
async def unassign_task(task_id: int, user_id: int, db: Session = Depends(get_db)):
    assignment = await db.exec(select(TaskAssignment).where(TaskAssignment.task_id == task_id, TaskAssignment.user_id == user_id))
    assignment = assignment.first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Task not assigned to this user.")
    
    await db.delete(assignment)
    await db.commit()
    return {"msg": "Task unassigned successfully"}
