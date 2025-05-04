import datetime
from typing import Optional

from sqlmodel import SQLModel, Field
from .complaint_status import ComplaintStatus


class ComplaintBase(SQLModel):
    complaint_text: str
    category: Optional[str] = None
    image_url: str = Field(nullable=True)
    latitude: float = Field(nullable=False)
    longitude: float = Field(nullable=False)
    description:str = Field(nullable=True)

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


class ComplaintQueryModel(SQLModel):
    category: Optional[str] = None
    limit: int = 10
    offset: int = 5
    status: Optional[ComplaintStatus] = ComplaintStatus.PENDING

