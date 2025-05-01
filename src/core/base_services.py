from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import AuthService
from src.complaints import ComplaintService
from src.tokens.token_service import TokenService
from src.core import redis_client
from src.users import UserService


class Services:
    def __init__(self, db: AsyncSession):
        self.token_service = TokenService(redis_client)

        self.complaint_service = ComplaintService(db)
        self.user = UserService(db)
        self.auth_service = AuthService(db, self.user,self.token_service)
