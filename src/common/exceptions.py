from fastapi import HTTPException
from pydantic import BaseModel
from starlette import status

class DatabaseError(HTTPException):
    def __init__(self, detail):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class IntegrityErrorException(DatabaseError):
    def __init__(self):
        super().__init__(
            detail='Integrity error'
        )

class BaseHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(BaseHTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code = status.HTTP_404_NOT_FOUND, detail=detail)


class ErrorResponse(BaseModel):
    detail: str