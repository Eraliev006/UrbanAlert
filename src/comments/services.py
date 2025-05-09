import logging
from src.comments.models import Comment
from src.comments.repositories import CommentRepositories
from src.comments.schemas import CommentCreate
from src.complaints import ComplaintService
from .exceptions import CommentNotFound
from src.notification import NotificationService
from src.notification.websocket_notification import WebSocketNotification
from src.websocket import manager

logger = logging.getLogger('fixkg.comment_service')

class CommentService:
    def __init__(
        self,
        comment_repo: CommentRepositories,
        complaint_service: ComplaintService,
        notification_service: NotificationService
    ):
        self._comment_repo = comment_repo
        self._complaint_service = complaint_service
        self._notification_service = notification_service

    async def create_comment(self, comment_data: CommentCreate, user_id: int) -> Comment:
        logger.debug('Creating comment for user_id=%d, complaint_id=%d', user_id, comment_data.complaint_id)
        complaint = await self._complaint_service.get_by_id(comment_data.complaint_id)

        comment = Comment(
            user_id=user_id,
            **comment_data.model_dump()
        )

        self._notification_service.set_strategy(WebSocketNotification(connection_manager=manager))
        await self._notification_service.send_notification(
            recipient=str(complaint.user_id),
            subject=f'New comment {complaint.complaint_text}',
            message=comment.content
        )

        logger.info('Comment created for user_id=%d, complaint_id=%d', user_id, comment_data.complaint_id)
        return await self._comment_repo.create(comment)

    async def get_comments_by_complaint(self, complaint_id: int) -> list[Comment]:
        logger.debug('Fetching comments for complaint_id=%d', complaint_id)
        await self._complaint_service.get_by_id(complaint_id)
        comments = await self._comment_repo.get_by_complaint_id(complaint_id)
        logger.info('Found %d comments for complaint_id=%d', len(comments), complaint_id)

        return comments

    async def delete_comment(self, comment_id: int, user_id: int) -> bool:
        logger.debug('Attempting to delete comment with comment_id=%d by user_id=%d', comment_id, user_id)
        comment = await self._comment_repo.get_by_id(comment_id)

        if not comment:
            logger.error('Comment with comment_id=%d not found', comment_id)
            raise CommentNotFound(comment_id)

        if comment.user_id != user_id:
            logger.warning('User_id=%d attempted to delete comment_id=%d that they do not own', user_id, comment_id)
            raise PermissionError("You do not have permission to delete this comment.")

        await self._comment_repo.delete(comment)
        logger.info('Comment with comment_id=%d deleted by user_id=%d', comment_id, user_id)

        return True
