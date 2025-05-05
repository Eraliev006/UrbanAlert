from sqlmodel import select

from src.common import BaseRepository, db_exception_handler
from .models import Comment


class CommentRepositories(BaseRepository):

    @db_exception_handler
    async def create(self, comment: Comment) -> Comment | None:
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)

        return comment

    @db_exception_handler
    async def get_by_complaint_id(self, complaint_id: int) -> list[Comment]:
        stmt = select(Comment).where(Comment.complaint_id == complaint_id)
        comments = await self.db.scalars(stmt)

        return list(comments)


    @db_exception_handler
    async def delete(self, comment: Comment) -> bool:
        await self.db.delete(comment)
        await self.db.commit()

        return True
