from starlette import status

from src.common import BaseHTTPException, AuthException


class PasswordIsIncorrect(AuthException):
    def __init__(self):
        super().__init__(detail='Password is incorrect')


class OTPCodeNotFoundOrExpired(BaseHTTPException):
    def __init__(self, email: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f'OTP code is not found or expired for email - {email}')


class OTPCodeIsWrong(BaseHTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail='OTP code is wrong')


