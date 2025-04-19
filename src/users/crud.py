from typing import Optional

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from src.common.exceptions import IntegrityErrorException, DatabaseError
from src.users import UserRead, UserCreate, User, UserWithIdNotFound, UserUpdate


async def create_user(db_session: AsyncSession, user: UserCreate) -> User:
    """
    Method to create user in database
    :param db_session: takes session to make transaction with database
    :param user: takes user: UserCreate
    :return: instance User, created in db
    """
    user = User(
        **user.model_dump()
    )

    try:
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    except IntegrityError:
        raise IntegrityErrorException

    except SQLAlchemyError:
        raise

async def _get_user_by_id(db_session: AsyncSession, user_id: int) -> User:
    try:
        user: Optional[User] = await db_session.get(User, user_id)
        return user
    except SQLAlchemyError:
        raise DatabaseError

async def get_user_by_id(db_session: AsyncSession, user_id: int) -> Optional[UserRead]:
    """
    Async function to get user_by_id
    :param db_session: take async db_session to make request to db
    :param user_id: take user ids to get user by this id
    :return: UserRead class, return created user or exception
    """
    user = await _get_user_by_id(db_session,user_id)
    if not user:
        raise UserWithIdNotFound(user_id)
    return UserRead(**user.model_dump())


async def update_user_by_id(db_session: AsyncSession, user_id: int, new_user_data: UserUpdate) -> Optional[UserRead]:
    """
    Async method to update user by id
    :param db_session: take async session to make request to db
    :param user_id: take user ids to get user by this id and update
    :param new_user_data: new user datas
    :return: UserRead class, return updated user or exception
    """
    user: Optional[User] = await _get_user_by_id(db_session, user_id)

    if not user:
        raise UserWithIdNotFound(user_id)

    for key, value in new_user_data.model_dump().items():
        setattr(user, key, value)

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return UserRead(**user.model_dump())

async def delete_user_by_id(db_session: AsyncSession, user_id: int) -> None:
    """
    Async def to delete user by id
    :param db_session: take async session to make request to db
    :param user_id: get id to get user by id and delete
    :return: None
    """
    user = await _get_user_by_id(db_session, user_id)

    if not user:
        raise UserWithIdNotFound(user_id)

    try:
        await db_session.delete(user)
        await db_session.commit()
    except SQLAlchemyError:
        raise 