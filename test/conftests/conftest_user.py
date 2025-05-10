from unittest.mock import MagicMock

import pytest
from src import User
from src.common import DatabaseError
from src.images import ImageService
from src.users import UserCreate, UserUpdate, UserService
from test import random_lower_string, random_email

from src.users import UserRepositories

@pytest.fixture(scope='function')
def user_repository(session) -> UserRepositories:
    return UserRepositories(session)

@pytest.fixture(scope='function')
def fake_user_create_data() -> UserCreate:
    return UserCreate(
        username = random_lower_string(),
        email = random_email(),
        password = random_lower_string(),
    )
@pytest.fixture(scope='function')
def fake_user_data() -> User:
    return User(
        username=random_lower_string(),
        email=random_email(),
        password=random_lower_string(),
    )

@pytest.fixture(scope='function')
def fake_user_update_data() -> UserUpdate:
    return UserUpdate(
        username = random_lower_string(),
        email = random_email(),
        avatar_url = random_lower_string()
    )

@pytest.fixture(scope='function')
def db_mock_raise_exception():
    db_mock = MagicMock()
    db_mock.scalar = MagicMock(side_effect=DatabaseError("SQL Error"))
    return db_mock

@pytest.fixture(scope='function')
def user_repository_with_mock(db_mock_raise_exception):
    return UserRepositories(db_mock_raise_exception)

@pytest.fixture(scope='function')
def image_service_mock() -> ImageService:
    image_service = MagicMock(spec=ImageService)
    image_service.save_user_avatar_image.return_value = "http://example.com/avatar.jpg"
    return image_service

@pytest.fixture(scope='function')
def user_service(user_repository, image_service_mock):
    return UserService(
        user_repo=user_repository,
        image_service=image_service_mock,
    )

@pytest.fixture(scope='function')
async def get_created_user(user_service, fake_user_create_data):
    created = await user_service.create_user(fake_user_create_data)
    return created
