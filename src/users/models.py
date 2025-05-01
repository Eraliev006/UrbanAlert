import datetime
from typing import Optional, TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src import Complaint


class BaseUser(SQLModel):
    username: str = Field(max_length=100, unique=True)
    email: EmailStr = Field(unique=True, index=True, nullable=False)
    avatar_url: Optional[str] = Field(nullable=True)

class User(BaseUser, table = True):
    __tablename__ = "user"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(primary_key=True, nullable=False, index=True)
    password: str = Field(nullable=False)
    is_verified: bool = Field(default=False, nullable=False)
    created_at: datetime.date = Field(default_factory=datetime.date.today)

    complaints: list["Complaint"] = Relationship(back_populates='user')

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



