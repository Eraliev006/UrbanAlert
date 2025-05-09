import logging
from sqlmodel import select

from src.common import BaseRepository, db_exception_handler
from src.comments.models import Comment


logger = logging.getLogger('fixkg.comment_repository')

class CommentRepositories(BaseRepository):

    @db_exception_handler
    async def create(self, comment: Comment) -> Comment | None:
        logger.debug('Creating comment: %s', comment)
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        logger.info('Comment created with ID: %d', comment.id)

        return comment

    @db_exception_handler
    async def get_by_complaint_id(self, complaint_id: int) -> list[Comment]:
        logger.debug('Getting comments for complaint_id: %d', complaint_id)
        stmt = select(Comment).where(Comment.complaint_id == complaint_id)
        comments = await self.db.scalars(stmt)
        logger.info('Found %d comments for complaint_id: %d', len(comments), complaint_id)

        return list(comments)

    @db_exception_handler
    async def delete(self, comment: Comment) -> bool:
        logger.debug('Deleting comment with ID: %d', comment.id)
        await self.db.delete(comment)
        await self.db.commit()
        logger.info('Comment with ID %d deleted', comment.id)

        return True

    @db_exception_handler
    async def get_by_id(self, comment_id: int) -> Comment:
        logger.debug('Getting comment with ID: %d', comment_id)
        stmt = select(Comment).where(Comment.id == comment_id)
        comment = await self.db.scalar(stmt)
        logger.info('Comment retrieved with ID: %d', comment.id if comment else 'Not Found')

        return comment
