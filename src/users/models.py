import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from src.users import BaseUser

if TYPE_CHECKING:
    from src import Complaint



class User(BaseUser, table = True):
    __tablename__ = "user"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(primary_key=True, nullable=False, index=True)
    password: str = Field(nullable=False)
    is_verified: bool = Field(default=False, nullable=False)
    created_at: datetime.date = Field(default_factory=datetime.date.today)

    complaints: list["Complaint"] = Relationship(
        back_populates='user',
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True
        }
    )





