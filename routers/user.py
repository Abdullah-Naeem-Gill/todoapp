from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from models import User, TaskAssignment
from database import get_db
from auth import verify_password, get_password_hash

router = APIRouter()

@router.post("/register", tags=["User"])
async def register(username: str, password: str, db: AsyncSession = Depends(get_db)):
    # Check for existing user
    existing_user = await db.exec(select(User).where(User.username == username))
    if existing_user.first():
        raise HTTPException(status_code=400, detail="Username already exists.")
    
    # Hash the password
    hashed_password = get_password_hash(password)
    
    # Create a new user instance
    new_user = User(username=username, hashed_password=hashed_password)
    
    # Add user to the session
    db.add(new_user)
    
    # Commit the session and handle potential errors
    try:
        await db.commit()  # Commit changes
        await db.refresh(new_user)  # Refresh to get updated user info
    except Exception as e:
        await db.rollback()  # Roll back if any error occurs
        raise HTTPException(status_code=500, detail="Could not register user.")

    return {"msg": "User registered successfully!"}

@router.post("/login", tags=["User"])
async def login(username: str, password: str, db: AsyncSession = Depends(get_db)):
    # Retrieve the user by username
    user = await db.exec(select(User).where(User.username == username))
    user = user.first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    
    return {"msg": f"Welcome back, {user.username}!"}

# @router.get("/tasks/{user_id}", tags=["User"])
# async def get_tasks(user_id: int, db: AsyncSession = Depends(get_db)):
#     # Retrieve the user by ID
#     user = await db.exec(select(User).where(User.id == user_id))
#     user = user.first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found.")
    
#     # Fetch tasks assigned to the user
#     assignments = await db.exec(select(TaskAssignment).where(TaskAssignment.user_id == user_id))
#     tasks = [assignment.task for assignment in assignments]
    
#     return {"tasks": tasks}  # Returning a structured response

@router.get("/users", tags=["User"])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    # Retrieve all users
    users = await db.exec(select(User))
    return {"users": [user for user in users]}  # Return a list of users

@router.get("/users/{user_id}", tags=["User"])
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    # Retrieve the user by ID
    user = await db.exec(select(User).where(User.id == user_id))
    user = user.first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    return {"user": user}  # Return the found user
