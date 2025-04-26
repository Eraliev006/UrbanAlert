import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class ComplaintBase(SQLModel):
    complaint_text: str
    category: Optional[str] = None
    priority: Optional[str] = None


class Complaint(ComplaintBase, table=True):
    __tablename__ = "complaint"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(primary_key=True, nullable=False, index=True)
    user_id: int
    status: str = Field(default="новая", nullable=False)
    created_at: datetime.date = Field(default_factory=datetime.date.today)
    updated_at: datetime.date = Field(default_factory=datetime.date.today)


class ComplaintCreate(ComplaintBase):
    user_id: int
    status: Optional[str] = "новая"


class ComplaintRead(ComplaintBase):
    id: int
    user_id: int
    status: str
    created_at: datetime.date
    updated_at: datetime.date


class ComplaintUpdate(SQLModel):
    status: Optional[str] = None
