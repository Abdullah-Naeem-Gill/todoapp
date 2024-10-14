# user.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from models import User, TaskAssignment
from database import get_db
from auth import verify_password, get_password_hash

router = APIRouter()

@router.post("/register", tags=["User"])
async def register(username: str, password: str, db: Session = Depends(get_db)):
    existing_user = await db.exec(select(User).where(User.username == username))
    if existing_user.first():
        raise HTTPException(status_code=400, detail="Username already exists.")
    
    hashed_password = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {"msg": "User registered successfully!"}

@router.post("/login", tags=["User"])
async def login(username: str, password: str, db: Session = Depends(get_db)):
    user = await db.exec(select(User).where(User.username == username))
    user = user.first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    
    return {"msg": f"Welcome back, {user.username}!"}

@router.get("/tasks/{user_id}", tags=["User"])
async def get_tasks(user_id: int, db: Session = Depends(get_db)):
    user = await db.exec(select(User).where(User.id == user_id))
    user = user.first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    assignments = await db.exec(select(TaskAssignment).where(TaskAssignment.user_id == user_id))
    tasks = [assignment.task for assignment in assignments]
    
    return tasks
