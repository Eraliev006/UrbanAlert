import datetime
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from src import User
from src.users import UserRepositories, UserService, UserCreate, UserUpdate


@pytest_asyncio.fixture(scope='function')
def user_repository(session):
    return UserRepositories(session)

@pytest_asyncio.fixture(scope='function')
async def fake_user():
    return User(username="test", email="test@example.com", password="123")


@pytest_asyncio.fixture(scope='function')
async def user(user_repository):
    created = await user_repository.create(User(username="test", email="test@example.com", password="123"))
    return created

@pytest_asyncio.fixture(scope='function')
def mock_user_repository():
    mock_repository = AsyncMock()
    return mock_repository

@pytest_asyncio.fixture(scope='function')
async def user_service(mock_user_repository, mock_image_service):
    return UserService(mock_user_repository,mock_image_service)

@pytest_asyncio.fixture(scope='function')
def mock_user():
    return User(
        id = 1,
        username="test",
        email="test@example.com",
        password="123",
        avatar_url = '',
        created_at = datetime.date.today()
    )

@pytest_asyncio.fixture
def mock_user_create():
    return UserCreate(
        username="test",
        email="test@example.com",
        password="123"
    )

@pytest.fixture
def mock_user_update():
    return UserUpdate(
        username="updated_user",
        email="updated@example.com"
    )

@pytest_asyncio.fixture(scope='function')
async def mock_user_service():
    service = AsyncMock()
    return service
