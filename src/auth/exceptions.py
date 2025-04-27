from fastapi import HTTPException
from starlette import status
from typing import Optional


class BaseHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class AuthException(BaseHTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class InvalidSignatureException(AuthException):
    def __init__(self):
        super().__init__(detail='Invalid token signature error')


class ExpiredTokenSignatureException(AuthException):
    def __init__(self):
        super().__init__(detail='Token expired')


class EmailAlreadyExists(BaseHTTPException):
    def __init__(self, email: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=f'Email - {email} already exists')


class EmailOrUsernameAlreadyExists(BaseHTTPException):
    def __init__(self, email: Optional[str], username: Optional[str]):
        detail = f'Email - {email} or username - {username} already exists'
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UserWithEmailNotFound(BaseHTTPException):
    def __init__(self, email: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f'Email - {email} is not found')


class PasswordIsIncorrect(AuthException):
    def __init__(self):
        super().__init__(detail='Password is incorrect')


class UserNotVerifyEmail(BaseHTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail='User is not verified email')


class UserWithUsernameNotFound(BaseHTTPException):
    def __init__(self, username: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f'Username - {username} is not found')


class OTPCodeNotFoundOrExpired(BaseHTTPException):
    def __init__(self, email: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f'OTP code is not found or expired for email - {email}')


class OTPCodeIsWrong(BaseHTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail='OTP code is wrong')


class UserAlreadyVerifiedEmail(BaseHTTPException):
    def __init__(self, email: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=f'User with email - {email} already verified')


class InvalidTokenType(AuthException):
    def __init__(self):
        super().__init__(detail='Token is of invalid type')


class RefreshTokenNotFound(AuthException):
    def __init__(self):
        super().__init__(detail='Refresh token not found')
