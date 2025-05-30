import datetime
from typing import Optional

from pydantic import EmailStr
from sqlmodel import SQLModel, Field


class BaseUser(SQLModel):
    username: str = Field(max_length=100, unique=True)
    email: EmailStr = Field(unique=True, index=True, nullable=False)

class UserCreate(BaseUser):
    password: str

class UserRead(BaseUser):
    id: int
    is_verified: bool
    avatar_url: Optional[str] = Field(nullable=True)
    created_at: datetime.date

class UserUpdate(SQLModel):
    username: str | None = None
    email: Optional[EmailStr] | None = None
