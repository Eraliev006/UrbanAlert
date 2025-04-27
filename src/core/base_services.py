from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import AuthService
from src.users import UserService


class Services:
    def __init__(self, db: AsyncSession):
        self.user = UserService(db)
        self.auth_service = AuthService(db, self.user)