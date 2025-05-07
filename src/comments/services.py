from src.comments.models import Comment
from src.comments.repositories import CommentRepositories
from src.comments.schemas import CommentCreate
from src.complaints import ComplaintService
from .exceptions import CommentNotFound
from src.notification import NotificationService
from src.notification.websocket_notification import WebSocketNotification
from src.websocket import manager


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
        return await self._comment_repo.create(comment)

    async def get_comments_by_complaint(self, complaint_id: int) -> list[Comment]:
        await self._complaint_service.get_by_id(complaint_id)
        return await self._comment_repo.get_by_complaint_id(complaint_id)

    async def delete_comment(self, comment_id: int, user_id: int) -> bool:
        comment = await self._comment_repo.get_by_id(comment_id)
        if not comment:
            raise CommentNotFound(comment_id)

        if comment.user_id != user_id:
            raise PermissionError("You do not have permission to delete this comment.")

        return await self._comment_repo.delete(comment)
