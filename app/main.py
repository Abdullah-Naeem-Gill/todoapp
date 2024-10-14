
from fastapi import FastAPI
from database import get_db, init_db
from routers import admin, user, task
from auth import router as auth_router

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_db()

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(admin.router, prefix="/admin")
app.include_router(user.router)
app.include_router(task.router, prefix="/task")
