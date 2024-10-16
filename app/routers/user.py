from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from models import User, TaskAssignment
from database import get_db
from auth import get_current_user, get_password_hash, verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class UserResponse(BaseModel):
    msg: str
    user_id: Optional[int] = None

class UserRead(BaseModel):
    id: int
    username: str

@router.post("/register", response_model=UserResponse, tags=["User"])
async def register(username: str, password: str, db: AsyncSession = Depends(get_db)):
  
    existing_user = await db.execute(select(User).where(User.username == username))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already exists.")
    
    
    new_user = User(username=username, hashed_password=get_password_hash(password))
    
  
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"msg": "User registered successfully!", "user_id": new_user.id}

@router.post("/login", tags=["User"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
   
    user = await db.execute(select(User).where(User.username == form_data.username))
    user = user.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/tasks/{user_id}", tags=["User"])
async def get_tasks(user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
   
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    
    assignments = await db.execute(select(TaskAssignment).where(TaskAssignment.user_id == user_id))
    tasks = [assignment.task for assignment in assignments]
    
    return {"tasks": tasks}  
@router.get("/users", response_model=List[UserRead], tags=["User"])
async def get_all_users(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    
    result = await db.execute(select(User))
    users = result.scalars().all()  

    
    user_read_list = [UserRead(id=user.id, username=user.username) for user in users]

    return user_read_list 


@router.get("/users/{user_id}", tags=["User"])
async def get_user_by_id(user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
   
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    return {"user": user} 
