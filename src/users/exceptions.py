from typing import Optional

from fastapi import HTTPException
from starlette import status

from src.common import BaseHTTPException, NotFoundException


class UserWithIdNotFound(HTTPException):
    def __init__(self, user_id: int):
        super().__init__(
            detail=f'User with {user_id}-ID not found',
            status_code=status.HTTP_404_NOT_FOUND
        )

class EmailAlreadyExists(BaseHTTPException):
    def __init__(self, email: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=f'Email - {email} already exists')


class EmailOrUsernameAlreadyExists(BaseHTTPException):
    def __init__(self, email: Optional[str], username: Optional[str]):
        detail = f'Email - {email} or username - {username} already exists'
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UserWithEmailNotFound(NotFoundException):
    def __init__(self, email: str):
        super().__init__(detail=f'Email - {email} is not found')

class UserNotVerifyEmail(BaseHTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail='User is not verified email')


class UserWithUsernameNotFound(NotFoundException):
    def __init__(self, username: str):
        super().__init__(detail=f'Username - {username} is not found')


class UserAlreadyVerifiedEmail(BaseHTTPException):
    def __init__(self, email: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=f'User with email - {email} already verified')

class UserWithUsernameAlreadyExists(BaseHTTPException):
    def __init__(self, username: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=f'User with username - {username} already exists')