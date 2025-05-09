import logging
from sqlmodel import select, or_

from src.users.models import User
from src.common import BaseRepository, db_exception_handler
from .schemas import UserUpdate

logger = logging.getLogger('fixkg.user_repo')

class UserRepositories(BaseRepository):

    @db_exception_handler
    async def get_by_id(self, user_id: int) -> User | None:
        logger.debug('get_by_id called with user_id=%d', user_id)
        stmt = select(User).where(User.id == user_id)
        user = await self.db.scalar(stmt)
        logger.debug('get_by_id result: %s', user)
        return user

    @db_exception_handler
    async def get_all(self) -> list[User]:
        logger.debug('get_all called')
        stmt = select(User)
        users = await self.db.scalars(stmt)
        result = list(users.all())
        logger.debug('get_all returned %d users', len(result))
        return result

    async def get_by_username(self, username: str) -> User | None:
        logger.debug('get_by_username called with username=%s', username)
        stmt = select(User).where(User.username == username)
        user = await self.db.scalar(stmt)
        logger.debug('get_by_username result: %s', user)
        return user

    @db_exception_handler
    async def get_by_email(self, email: str) -> User | None:
        logger.debug('get_by_email called with email=%s', email)
        stmt = select(User).where(User.email == email)
        user = await self.db.scalar(stmt)
        logger.debug('get_by_email result: %s', user)
        return user

    @db_exception_handler
    async def get_by_email_or_username(self, email: str = None, username: str = None) -> User | None:
        logger.debug('get_by_email_or_username called with email=%s, username=%s', email, username)
        stmt = select(User).where(or_(User.email == email, User.username == username))
        user = await self.db.scalar(stmt)
        logger.debug('get_by_email_or_username result: %s', user)
        return user

    @db_exception_handler
    async def create(self, user: User) -> User:
        logger.debug('create called with user: %s', user)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        logger.info('User created with id=%d', user.id)
        return user

    @db_exception_handler
    async def update(self, user: User, new_data: UserUpdate) -> User:
        logger.debug('update called for user_id=%d with new_data=%s', user.id, new_data)
        updated_instance = await self.update_instance(
            instance=user,
            new_data=new_data
        )
        logger.debug('update result: %s', updated_instance)
        return updated_instance

    @db_exception_handler
    async def delete(self, user: User):
        logger.debug('delete called for user_id=%d', user.id)
        await self.db.delete(user)
        await self.db.commit()
        logger.info('User deleted with id=%d', user.id)
        return None

    @db_exception_handler
    async def set_verified(self, user: User, verified: bool = True) -> User:
        logger.debug('set_verified called for user_id=%d with verified=%s', user.id, verified)
        user.is_verified = verified
        await self.db.commit()
        await self.db.refresh(user)
        logger.debug('set_verified completed for user_id=%d', user.id)
        return user

    @db_exception_handler
    async def save_user_avatar(self, avatar_url: str, user_id: int) -> User:
        logger.debug('save_user_avatar called for user_id=%d with avatar_url=%s', user_id, avatar_url)
        user = await self.get_by_id(user_id)
        user.avatar_url = avatar_url
        await self.db.commit()
        await self.db.refresh(user)
        logger.info('Avatar updated for user_id=%d', user_id)
        return user
