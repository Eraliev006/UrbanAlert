from pydantic import BaseModel


class CommentCreate(BaseModel):
    user_id: int
    complaint_id: int
    content: str
