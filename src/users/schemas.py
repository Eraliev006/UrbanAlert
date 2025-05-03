import datetime
from typing import Optional

from pydantic import EmailStr
from sqlmodel import SQLModel, Field


class BaseUser(SQLModel):
    username: str = Field(max_length=100, unique=True)
    email: EmailStr = Field(unique=True, index=True, nullable=False)
    avatar_url: Optional[str] = Field(nullable=True)

class UserCreate(BaseUser):
    password: str

class UserRead(BaseUser):
    id: int
    is_verified: bool
    created_at: datetime.date

class UserUpdate(SQLModel):
    username: str
    email: Optional[EmailStr]
    avatar_url: Optional[str]
    is_verified: Optional[bool] = False