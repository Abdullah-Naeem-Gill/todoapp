# models.py
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class UserRoleLink(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    role_id: Optional[int] = Field(default=None, foreign_key="role.id", primary_key=True)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(nullable=False, unique=True)
    hashed_password: str = Field(nullable=False)

    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRoleLink)
    tasks: List["TaskAssignment"] = Relationship(back_populates="user")

class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)

    users: List["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)

    assignments: List["TaskAssignment"] = Relationship(back_populates="task")

class TaskAssignment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    status: str = Field(default="pending")

    user: "User" = Relationship(back_populates="tasks")
    task: "Task" = Relationship(back_populates="assignments")
