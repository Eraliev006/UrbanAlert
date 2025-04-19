from fastapi import HTTPException
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

