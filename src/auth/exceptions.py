from starlette import status

from src.common import BaseHTTPException


class AuthException(BaseHTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class InvalidSignatureException(AuthException):
    def __init__(self):
        super().__init__(detail='Invalid token signature error')


class ExpiredTokenSignatureException(AuthException):
    def __init__(self):
        super().__init__(detail='Token expired')


class PasswordIsIncorrect(AuthException):
    def __init__(self):
        super().__init__(detail='Password is incorrect')


class OTPCodeNotFoundOrExpired(BaseHTTPException):
    def __init__(self, email: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f'OTP code is not found or expired for email - {email}')


class OTPCodeIsWrong(BaseHTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail='OTP code is wrong')


class InvalidTokenType(AuthException):
    def __init__(self):
        super().__init__(detail='Token is of invalid type')


class RefreshTokenNotFound(AuthException):
    def __init__(self):
        super().__init__(detail='Refresh token not found')
