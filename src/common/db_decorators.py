from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from src.common import DatabaseError

def db_exception_handler(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise DatabaseError(f"Database operation failed: {e}") from e
    return wrapper
