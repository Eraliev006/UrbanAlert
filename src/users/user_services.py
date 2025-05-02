from typing import Optional
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.common import IntegrityErrorException, DatabaseError
from src.users import UserRead, UserCreate, User, UserWithIdNotFound, UserUpdate, UserWithUsernameAlreadyExists, \
    EmailAlreadyExists


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_users(self) -> Optional[list[UserRead]]:
        """
        Method to get all users.
        :return: List of UserRead or None
        """
        try:
            stmt = select(User)
            users = await self.db.scalars(stmt)
            return [UserRead(**user.model_dump()) for user in users]
        except SQLAlchemyError:
            raise DatabaseError('Error with DB while getting all users')

    async def create_user(self, user: UserCreate) -> User:
        """
        Method to create a new user in the database.
        :param user: UserCreate instance containing the user data.
        :return: Created User instance.
        """
        new_user = User(**user.model_dump())
        try:
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            return new_user
        except IntegrityError:
            raise IntegrityErrorException
        except SQLAlchemyError:
            raise DatabaseError('Error with DB while creating user')

    async def _get_user_by_id(self, user_id: int) -> Optional[User]:
        try:
            user = await self.db.get(User, user_id)
            return user
        except SQLAlchemyError:
            raise DatabaseError('Error with DB while getting user by ID')

    async def get_user_by_id(self, user_id: int) -> Optional[UserRead]:
        """
        Async function to get user by ID.
        :param user_id: ID of the user.
        :return: UserRead instance or raises UserWithIdNotFound exception.
        """
        user = await self._get_user_by_id(user_id)
        if not user:
            raise UserWithIdNotFound(user_id)
        return UserRead(**user.model_dump())

    async def _check_email_and_username_to_unique(self, email: Optional[str] = None, username: Optional[str] = None):
        if email:
            user_by_email = await self.get_user_by_email(email)
            if user_by_email:
                raise EmailAlreadyExists(email)
        if username:
            user_by_username = await self.get_user_by_username(username)
            if user_by_username:
                raise UserWithUsernameAlreadyExists(username)

    async def update_user_by_id(self, user_id: int, new_user_data: UserUpdate) -> Optional[UserRead]:
        """
        Async method to update user data by user ID.
        :param user_id: ID of the user to update.
        :param new_user_data: Data to update the user.
        :return: Updated UserRead instance.
        """
        user = await self._get_user_by_id(user_id)
        if not user:
            raise UserWithIdNotFound(user_id)

        # Only check unique constraint if email or username is being updated
        if new_user_data.email:
            await self._check_email_and_username_to_unique(email=new_user_data.email)
        if new_user_data.username:
            await self._check_email_and_username_to_unique(username=new_user_data.username)

        # Update user fields
        for key, value in new_user_data.model_dump().items():
            if value is not None:  # Avoid updating fields with None values
                setattr(user, key, value)

        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return UserRead(**user.model_dump())
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseError('Error with DB while updating user')

    async def delete_user_by_id(self, user_id: int) -> None:
        """
        Async method to delete user by ID.
        :param user_id: ID of the user to delete.
        """
        user = await self._get_user_by_id(user_id)
        if not user:
            raise UserWithIdNotFound(user_id)

        try:
            await self.db.delete(user)
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseError('Error with DB while deleting user')

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Async method to get user by email.
        :param email: User's email.
        :return: User instance or None.
        """
        try:
            stmt = select(User).where(User.email == email)
            user = await self.db.scalar(stmt)
            return user
        except SQLAlchemyError:
            raise DatabaseError('Error with DB while getting user by email')

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Async method to get user by username.
        :param username: User's username.
        :return: User instance or None.
        """
        try:
            stmt = select(User).where(User.username == username)
            user = await self.db.scalar(stmt)
            return user
        except SQLAlchemyError:
            raise DatabaseError('Error with DB while getting user by username')

    async def change_user_is_verify_status(self, user: User):
        """
        Async method to change user verification status.
        :param user: User instance to change status.
        """
        user.is_verified = True
        try:
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseError('Error with DB while changing user status')

    async def get_user_by_email_or_username(self, email: Optional[str], username: Optional[str]) -> Optional[User]:
        """
        Async method to get user by email or username.
        :param email: User's email.
        :param username: User's username.
        :return: User instance or None.
        """
        try:
            stmt = select(User).where(or_(User.username == username, User.email == email))
            user = await self.db.scalar(stmt)
            return user
        except SQLAlchemyError:
            raise DatabaseError('Error with DB while getting user by email or username')
