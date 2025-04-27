from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import AuthService
from src.auth.tokens.token_repository import TokenRepository
from src.core import redis_client
from src.users import UserService


class Services:
    def __init__(self, db: AsyncSession):
        self.token_repo = TokenRepository(redis_client)

        self.user = UserService(db)
        self.auth_service = AuthService(db, self.user,self.token_repo)