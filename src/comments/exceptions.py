from starlette import status

from src.common import BaseHTTPException


class CommentNotFound(BaseHTTPException):
    def __init__(self, comment_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Comment with id {comment_id} not found'
        )