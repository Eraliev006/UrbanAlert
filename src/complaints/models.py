import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from .schemas import ComplaintBase
from .complaint_status import ComplaintStatus

if TYPE_CHECKING:
    from src import User, Comment


class Complaint(ComplaintBase, table=True):
    __tablename__ = "complaint"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(primary_key=True, nullable=False, index=True)
    user_id: int = Field(foreign_key='user.id', ondelete="CASCADE")
    status: ComplaintStatus = Field(default=ComplaintStatus.PENDING, nullable=False)
    created_at: datetime.date = Field(default_factory=datetime.date.today)
    updated_at: datetime.date = Field(default_factory=datetime.date.today)

    user: "User" = Relationship(back_populates='complaints')
    comments: list["Comment"] = Relationship(back_populates='complaint')

