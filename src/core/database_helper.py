from logging import getLogger
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core import settings

logger = getLogger('fixkg.database_helper')

class DatabaseHelper:
    def __init__(
            self,
            url: str,
            echo: bool = True,
            pool_size: int = 5,
            max_overflow: int = 10,
            echo_pool: bool = False
    ):
        logger.debug('Initializing DatabaseHelper with URL: %s', url)

        self.async_engine = create_async_engine(
            url=url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo_pool=echo_pool
        )

        self.session_factory = async_sessionmaker(
            bind=self.async_engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

        logger.info('DatabaseHelper initialized successfully with async engine')

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        logger.debug('Getting database session')
        async with self.session_factory() as session:
            logger.debug('Session successfully retrieved')
            yield session
        logger.debug('Session closed')

    async def dispose(self):
        logger.debug('Disposing async engine')
        await self.async_engine.dispose()
        logger.info('Async engine disposed successfully')


# Example usage of DatabaseHelper:
database_helper = DatabaseHelper(
    url=settings.database.get_url()
)
