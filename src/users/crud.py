from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from src.common.exceptions import IntegrityErrorException
from src.users import UserRead, UserCreate, User


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

