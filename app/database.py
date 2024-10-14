# database.py
import os
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Use environment variable for the database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://abdullah:abdullah042@localhost/todo")

# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create an async session local
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
