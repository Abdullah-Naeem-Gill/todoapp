from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from models import User
from database import get_db, init_db
from routers import admin, user, task

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_db()

@app.post("/signup/")
async def signup(username: str, password: str, db: Session = Depends(get_db)):
    existing_user = await db.exec(select(User).where(User.username == username))
    
    if existing_user.first():
        raise HTTPException(status_code=400, detail="Username already registered")
    

    new_user = User(username=username, hashed_password=password)  
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"msg": "User created successfully", "user_id": new_user.id}  

@app.post("/login")
async def login(username: str, password: str, db: Session = Depends(get_db)):
   
    user = await db.exec(select(User).where(User.username == username))
    user = user.first()

    
    if not user or user.hashed_password != password:  
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {"msg": f"Welcome {user.username}!", "user_id": user.id}

@app.get("/users/me/{user_id}")
async def read_users_me(user_id: int, db: Session = Depends(get_db)):

    user = await db.exec(select(User).where(User.id == user_id))
    user = user.first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"username": user.username, "user_id": user.id}

app.include_router(admin.router, prefix="/admin")
app.include_router(user.router)
app.include_router(task.router, prefix="/task")
