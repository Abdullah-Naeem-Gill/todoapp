from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from auth import hash_password, create_access_token, verify_password, oauth2_scheme, verify_token
from models import User
from database import get_db, init_db

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_db()

@app.post("/signup/")
async def signup(username: str, password: str, db: Session = Depends(get_db)):
    existing_user = await db.exec(select(User).where(User.username == username))
    
    if existing_user.first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = User(username=username, hashed_password=hash_password(password))
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"msg": "User created successfully"}

@app.post("/token", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    user = await db.exec(select(User).where(User.username == form_data.username))
    user = user.first() 

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_token(token, credentials_exception)
    return {"username": payload.get("sub")}
