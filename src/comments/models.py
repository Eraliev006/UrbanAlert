from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.users.models import User
    from src import Complaint


class Comment(SQLModel, table=True):
    __tablename__ = 'comments'
    __table_args__ = {"extend_existing": True}

    id: int | None = Field(primary_key=True, nullable=False, index=True)
    user_id: int = Field(foreign_key='user.id', ondelete='CASCADE', nullable=False)
    complaint_id: int = Field(foreign_key='complaint.id', ondelete='CASCADE', nullable=False)
    content:str = Field(nullable=False)

    user: Optional["User"] = Relationship()
    complaint: "Complaint" = Relationship(back_populates="comments")