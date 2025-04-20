import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core import settings
from src.users import UserCreate
from test import random_lower_string, random_email


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

@pytest.fixture(scope='function')
def fake_user_create_data() -> UserCreate:
    return UserCreate(
        first_name = random_lower_string(),
        last_name = random_lower_string(),
        email = random_email(),
        password = random_lower_string(),
        avatar_url = random_lower_string()
    )
