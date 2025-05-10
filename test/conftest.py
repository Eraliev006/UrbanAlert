import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


from src.core import settings


pytest_plugins = [
    "test.conftests.conftest_user",
]

@pytest_asyncio.fixture(scope='function')
async def session():
    async_engine = create_async_engine(
        url=settings.database.get_url(),
        echo = True,
        echo_pool = False,
        pool_size = 5,
        max_overflow = 10
    )

    AsyncSessionLocal = async_sessionmaker(
        bind = async_engine,
        autoflush = False,
        expire_on_commit = False,
        autocommit = False
    )

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
