import pytest

from src import User
from src.users import UserRepositories


@pytest.fixture(scope='function')
def user_repository(session):
    return UserRepositories(session)

@pytest.fixture(scope='function')
async def fake_user():
    return User(username="test", email="test@example.com", password="123")


@pytest.fixture(scope='function')
async def user(user_repository):
    created = await user_repository.create(User(username="test", email="test@example.com", password="123"))
    return created