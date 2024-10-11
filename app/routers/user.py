from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from models import User, TaskAssignment
from database import get_db

router = APIRouter()

@router.post("/register", tags=["User"])
async def register(username: str, password: str, db: Session = Depends(get_db)):
    existing_user = await db.exec(select(User).where(User.username == username))
    if existing_user.first():
        raise HTTPException(status_code=400, detail="Username already exists.")
    
    new_user = User(username=username, hashed_password=password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"msg": "User registered successfully", "user_id": new_user.id}

@router.post("/login", tags=["User"])
async def login(username: str, password: str, db: Session = Depends(get_db)):
    user = await db.exec(select(User).where(User.username == username))
    user = user.first()
    if not user or user.hashed_password != password:  
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    
    return {"msg": f"Welcome {user.username}!", "user_id": user.id}

@router.get("/tasks/{user_id}", tags=["User"])
async def get_tasks(user_id: int, db: Session = Depends(get_db)):
    user = await db.exec(select(User).where(User.id == user_id))
    user = user.first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    # Retrieve tasks assigned to the user
    assignments = await db.exec(select(TaskAssignment).where(TaskAssignment.user_id == user_id))
    tasks = [assignment.task for assignment in assignments]
    return tasks
