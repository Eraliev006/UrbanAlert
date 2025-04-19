from fastapi import HTTPException
from starlette import status


class UserWithIdNotFound(HTTPException):
    def __init__(self, user_id: int):
        super().__init__(
            detail=f'User with {user_id}-ID not found',
            status_code=status.HTTP_404_NOT_FOUND
        )