from typing import Annotated

from fastapi import APIRouter, Depends

from src.comments.schemas import CommentCreate
from src.comments.services import CommentService
from src.core import get_current_user
from src.core.dependencies import get_comment_service
from src.users import UserRead

router = APIRouter(
    tags=['Comment']
)

COMMENT_SERVICE_DEP = Annotated[CommentService, Depends(get_comment_service)]

@router.get(
    '/complaint/{complaint_id}/comments',
    dependencies=[Depends(get_current_user)]
)
async def get_comment_by_complaint_id(
        comment_service: COMMENT_SERVICE_DEP,
        complaint_id: int
):
    return await comment_service.get_comments_by_complaint(complaint_id)


@router.post('/comments')
async def create_comment(
        comment: CommentCreate,
        comment_service: COMMENT_SERVICE_DEP,
        current_user: UserRead = Depends(get_current_user)
):
    return await comment_service.create_comment(comment, current_user.id)