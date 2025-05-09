import logging
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from src.common import DatabaseError

logger = logging.getLogger('fixkg.db_exception_handler')

def db_exception_handler(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            logger.debug('Executing function: %s with arguments: %s, %s', func.__name__, args, kwargs)
            result = await func(self, *args, **kwargs)
            logger.info('Function %s executed successfully', func.__name__)
            return result
        except SQLAlchemyError as e:
            logger.error('Database operation failed in function %s: %s', func.__name__, e)
            await self.db.rollback()
            raise DatabaseError(f"Database operation failed: {e}") from e
    return wrapper
