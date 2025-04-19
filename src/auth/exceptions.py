from fastapi import HTTPException
from starlette import status


class AuthException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class InvalidSignatureException(AuthException):
    def __init__(self):
        super().__init__(
            detail='Invalid token signature error',
        )

class ExpiredTokenSignatureException(AuthException):
    def __init__(self):
        super().__init__(
            detail='Token expired',
        )

class EmailAlreadyExists(HTTPException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Email - {email} already exists'
        )