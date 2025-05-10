import datetime
from unittest.mock import AsyncMock

import pytest

from src import User
from src.users import  EmailOrUsernameAlreadyExists, UserWithIdNotFound


class TestUserService:
    @staticmethod
    @pytest.mark.asyncio
    async def test_create_user(user_service, fake_user_create_data, get_created_user):
        assert get_created_user
        assert fake_user_create_data.username == get_created_user.username

    @staticmethod
    @pytest.mark.asyncio
    async def test_create_user_failed_email_or_username_exists(user_service, get_created_user):

        with pytest.raises(EmailOrUsernameAlreadyExists):
            await user_service.create_user(get_created_user)

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_by_id(user_service, fake_user_create_data, get_created_user):
        user = await user_service.get_user_by_id(get_created_user.id)

        assert user
        assert user.username == get_created_user.username


    @staticmethod
    @pytest.mark.asyncio
    async def test_get_by_id_failed_not_found(user_service):

        with pytest.raises(UserWithIdNotFound):
            await user_service.get_user_by_id(-1)

    @staticmethod
    @pytest.mark.asyncio
    async def test_update_user_by_id_success(user_service, fake_user_update_data):
        user_id = 1
        old_user = User(
            id=user_id,
            username="testuser",
            email="testuser@example.com",
            is_verified=False,
            avatar_url="https://oldavatar.com",
            created_at=datetime.date.today()
        )

        user_service._user_repo.get_by_id = AsyncMock(return_value=old_user)

        user_service._check_if_user_exists = AsyncMock(return_value=False)

        updated_user = User(
            id=user_id,
            username=fake_user_update_data.username,
            email=fake_user_update_data.email,
            avatar_url=fake_user_update_data.avatar_url,
            is_verified=False,
            created_at=datetime.date.today()
        )
        user_service._user_repo.update = AsyncMock(return_value=updated_user)

        updated_user_result = await user_service.update_user_by_id(user_id, fake_user_update_data)

        assert updated_user_result.username == fake_user_update_data.username
        assert updated_user_result.email == fake_user_update_data.email
        assert updated_user_result.avatar_url == fake_user_update_data.avatar_url

        user_service._user_repo.update.assert_called_once_with(
            user=old_user,
            new_data=fake_user_update_data
        )
    @staticmethod
    @pytest.mark.asyncio
    async def test_delete_user(user_service, fake_user_create_data, get_created_user):

        await user_service.delete_user_by_id(get_created_user.id)
        with pytest.raises(UserWithIdNotFound):
            await user_service.get_user_by_id(get_created_user.id)
