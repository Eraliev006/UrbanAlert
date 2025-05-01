from starlette import status

from src.common import NotFoundException, BaseHTTPException


class ComplaintWithIdNotFound(NotFoundException):
    def __init__(self, complaint_id: int):
        super().__init__(detail=f'Comaplaint with ID - {complaint_id} not found')


class AccessDenied(BaseHTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to access this complaint.")