from sqlmodel import select, or_

from .models import User
from src.common import BaseRepository, db_exception_handler
from .schemas import UserUpdate


class UserRepositories(BaseRepository):

    @db_exception_handler
    async def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        user = await self.db.scalar(stmt)

        return user

    @db_exception_handler
    async def get_all(self) -> list[User]:
        stmt = select(User)
        users = await self.db.scalars(stmt)

        return list(users.all())

    @db_exception_handler
    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        user = await self.db.scalar(stmt)

        return user

    @db_exception_handler
    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        user = await self.db.scalar(stmt)

        return user

    @db_exception_handler
    async def get_by_email_or_username(self, email: str = None, username:str = None) -> User | None:
        stmt = select(User).where(or_(User.email == email, User.username == username))
        user = await self.db.scalar(stmt)

        return user

    @db_exception_handler
    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    @db_exception_handler
    async def update(self, user: User, new_data: UserUpdate) -> User:
        updated_instance = await self.update_instance(
            instance=user,
            new_data=new_data
        )

        return updated_instance

    @db_exception_handler
    async def delete(self, user: User):
        await self.db.delete(user)
        await self.db.commit()

        return None

    @db_exception_handler
    async def set_verified(self, user:User, verified: bool = True) -> User:
        user.is_verified = verified
        await self.db.commit()
        await self.db.refresh(user)

        return user