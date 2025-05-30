import datetime
from typing import Optional

from sqlmodel import SQLModel, Field
from .complaint_status import ComplaintStatus
from src.comments.schemas import CommentRead


class ComplaintBase(SQLModel):
    complaint_text: str
    category: Optional[str] = None
    latitude: float = Field(nullable=False)
    longitude: float = Field(nullable=False)
    description:str = Field(nullable=True)

class ComplaintCreate(ComplaintBase):
    status: ComplaintStatus = Field(default=ComplaintStatus.PENDING)


class ComplaintRead(ComplaintBase):
    id: int
    user_id: int
    status: ComplaintStatus
    image_url: str | None = Field(nullable=True)
    created_at: datetime.date
    updated_at: datetime.date

class ComplaintReadDetailsSchemas(ComplaintRead):
    comments: list[CommentRead] = []

class ComplaintUpdate(SQLModel):
    status: Optional[ComplaintStatus] = ComplaintStatus.PENDING


class ComplaintQueryModel(SQLModel):
    category: Optional[str] = None
    limit: int = 10
    offset: int = 0
    status: Optional[ComplaintStatus] = ComplaintStatus.PENDING

