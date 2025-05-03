from sqlalchemy.exc import SQLAlchemyError

from src.common import DatabaseError


def db_exception_handler(func):
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise DatabaseError(f'error with database: {e}')
    return wrapper