import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from .complaint_status import ComplaintStatus

if TYPE_CHECKING:
    from src import User


class ComplaintBase(SQLModel):
    complaint_text: str
    category: Optional[str] = None
    image_url: str = Field(nullable=True)
    latitude: float = Field(nullable=False)
    longitude: float = Field(nullable=False)
    description:str = Field(nullable=True)


class Complaint(ComplaintBase, table=True):
    __tablename__ = "complaint"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(primary_key=True, nullable=False, index=True)
    user_id: int = Field(foreign_key='user.id', ondelete="CASCADE")
    status: ComplaintStatus = Field(default=ComplaintStatus.PENDING, nullable=False)
    created_at: datetime.date = Field(default_factory=datetime.date.today)
    updated_at: datetime.date = Field(default_factory=datetime.date.today)

    user: "User" = Relationship(back_populates='complaints')


class ComplaintCreate(ComplaintBase):
    status: Optional[ComplaintStatus] = Field(default=ComplaintStatus.PENDING)


class ComplaintRead(ComplaintBase):
    id: int
    user_id: int
    status: ComplaintStatus
    created_at: datetime.date
    updated_at: datetime.date


class ComplaintUpdate(SQLModel):
    status: Optional[ComplaintStatus] = ComplaintStatus.PENDING
