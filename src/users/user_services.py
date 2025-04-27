
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.common import IntegrityErrorException, DatabaseError
from src.users import UserRead, UserCreate, User, UserWithIdNotFound, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_users(self) -> Optional[list[UserRead]]:
        """
        Method to get all user.
        Return list[UserRead] | None
        """
        try:
            stmt = select(User)
            users = await self.db.scalars(stmt)
            return [UserRead(**user.model_dump()) for user in users]

        except SQLAlchemyError:
            raise DatabaseError('Error with db while getting all users')

    async def create_user(self,user: UserCreate) -> User:
        """
        Method to create user in database
        :param user: takes user: UserCreate
        :return: instance User, created in db
        """
        user = User(
            **user.model_dump()
        )

        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user

        except IntegrityError:
            raise IntegrityErrorException

        except SQLAlchemyError:
            raise DatabaseError('Error with DB while creating user')

    async def _get_user_by_id(self, user_id: int) -> User:
        try:
            user: Optional[User] = await self.db.get(User, user_id)
            return user
        except SQLAlchemyError:
            raise DatabaseError('Error with db while getting user by id')

    async def get_user_by_id(self, user_id: int) -> Optional[UserRead]:
        """
        Async function to get user_by_id
        :param user_id: take user ids to get user by this id
        :return: UserRead class, return created user or exception
        """
        user = await self._get_user_by_id(user_id)
        if not user:
            raise UserWithIdNotFound(user_id)
        return UserRead(**user.model_dump())

    async def update_user_by_id(self, user_id: int, new_user_data: UserUpdate) -> Optional[
        UserRead]:
        """
        Async method to update user by id
        :param user_id: take user ids to get user by this id and update
        :param new_user_data: new user datas
        :return: UserRead class, return updated user or exception
        """
        user: Optional[User] = await self._get_user_by_id(user_id)

        if not user:
            raise UserWithIdNotFound(user_id)

        for key, value in new_user_data.model_dump().items():
            setattr(user, key, value)

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return UserRead(**user.model_dump())

    async def delete_user_by_id(self, user_id: int) -> None:
        """
        Async def to delete user by id
        :param user_id: get id to get user by id and delete
        :return: None
        """
        user = await self._get_user_by_id(user_id)

        if not user:
            raise UserWithIdNotFound(user_id)

        try:
            await self.db.delete(user)
            await self.db.commit()
        except SQLAlchemyError:
            raise DatabaseError('Error with db while deleting user by id')

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Async def to get user by email
        :param email: get email to get user by email
        :return: User
        """
        try:
            stmt = select(User).where(User.email == email)
            user: Optional[User] = await self.db.scalar(stmt)
            return user
        except SQLAlchemyError:
            raise DatabaseError('Error with db while getting user by email')

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Async def to get user by username
        :param username: get username to get user by username
        :return: User
        """
        try:
            stmt = select(User).where(User.username == username)
            user: Optional[User] = await self.db.scalar(stmt)
            return user
        except SQLAlchemyError:
            raise DatabaseError('Error with db while getting user by username')

    async def change_user_is_verify_status(
            self,
            user: User
    ):
        """
        Async def to get change user status
        :param user: instance of user to change his status
        """
        user.is_verified = True
        try:
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseError('Error with db while change user status')

    async def get_user_by_email_or_username(self, email: Optional[str],username: Optional[str]) -> Optional[User]:
        """
        Async def to get user by email or username
        :param username: get username to get user by username
        :param email: get email to get user by email
        :return: User
        """
        try:
            stmt = select(User).where(or_(User.username == username, User.email == email))
            user: Optional[User] = await self.db.scalar(stmt)
            return user
        except SQLAlchemyError:
            raise DatabaseError('Error with db while getting user by username or email')