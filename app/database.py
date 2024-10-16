import os
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://abdullah:abdullah042@localhost/todo")

engine = create_async_engine(DATABASE_URL, echo=True)


async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        
        await conn.run_sync(SQLModel.metadata.create_all)
