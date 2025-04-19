from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core import settings


class DatabaseHelper:
    def __init__(
            self,
            url: str,
            echo: bool = True,
            pool_size: int = 5,
            max_overflow: int = 10,
            echo_pool: bool = False
    ):

        self.async_engine = create_async_engine(
            url = url,
            echo = echo,
            pool_size = pool_size,
            max_overflow = max_overflow,
            echo_pool = echo_pool
        )

        self.session_factory = async_sessionmaker(
            bind=self.async_engine,
            autoflush=False,
            autocommit = False,
            expire_on_commit = False
        )

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
             yield session

    async def dispose(self):
        await self.async_engine.dispose()


database_helper = DatabaseHelper(
    url = settings.db.get_url()
)