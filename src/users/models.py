import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class BaseUser(SQLModel):
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    avatar_url: Optional[str] = Field(nullable=True)

class User(BaseUser, table = True):
    id: Optional[int] = Field(primary_key=True, nullable=False, index=True)
    email: EmailStr = Field(unique=True, index=True, nullable=False)
    password: str = Field(nullable=False)
    created_at: datetime.date

class UserCreate(BaseUser):
    password: str

class UserRead(BaseUser):
    id: int
    created_at: datetime.date

class UserUpdate(BaseUser):
    pass



