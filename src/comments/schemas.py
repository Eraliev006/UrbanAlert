from pydantic import BaseModel


class CommentCreate(BaseModel):
    complaint_id: int
    content: str


class CommentRead(BaseModel):
    id: int
    user_id: int
    complaint_id: int
    content: str