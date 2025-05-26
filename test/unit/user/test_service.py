from unittest import mock
from unittest.mock import AsyncMock

import pytest
from fastapi import UploadFile

from src.users import EmailOrUsernameAlreadyExists, UserWithIdNotFound, UserWithUsernameNotFound, UserWithEmailNotFound


class TestUserService:

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_successful(self, user_service, mock_user_repository, mock_user, mock_user_create):
        mock_user_repository.get_by_email_or_username.return_value = None
        mock_user_repository.create.return_value = mock_user

        result = await user_service.create_user(mock_user_create)

        mock_user_repository.create.assert_called_once_with(mock.ANY)
        assert result.id == mock_user.id
        assert result.email == mock_user.email


    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_failed_email_or_username_exists(self, user_service, mock_user_repository, mock_user, mock_user_create):
        mock_user_repository.get_by_email_or_username.return_value = mock_user

        with pytest.raises(EmailOrUsernameAlreadyExists):
            await user_service.create_user(mock_user_create)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_id_successful(self, user_service, mock_user_repository, mock_user):
        user_id = 1
        mock_user_repository.get_by_id.return_value = mock_user

        result = await user_service.get_user_by_id(user_id)

        mock_user_repository.get_by_id.assert_called_once_with(1)
        assert result.email == mock_user.email

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_id_failed(self, user_service, mock_user_repository, mock_user):
        user_id = 1
        mock_user_repository.get_by_id.return_value = None

        with pytest.raises(UserWithIdNotFound):
            await user_service.get_user_by_id(user_id)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_all_users(self, user_service, mock_user_repository, mock_user):
        mock_user_repository.get_all.return_value = [mock_user]

        result = await user_service.get_all_users()

        mock_user_repository.get_all.assert_called_once()
        assert len(result) == 1
        assert result[0].id == mock_user.id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_user_successful(self, user_service, mock_user_repository, mock_user, mock_user_update):
        mock_user_repository.get_by_id.return_value = mock_user
        mock_user_repository.get_by_email_or_username.return_value = None
        mock_user_repository.update.return_value = mock_user

        result = await user_service.update_user_by_id(1, mock_user_update)

        mock_user_repository.update.assert_called_once()
        assert result.id == mock_user.id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_user_failed_not_found(self, user_service, mock_user_repository, mock_user_update):
        mock_user_repository.get_by_id.return_value = None

        with pytest.raises(UserWithIdNotFound):
            await user_service.update_user_by_id(1, mock_user_update)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_user_failed_duplicate(self, user_service, mock_user_repository, mock_user, mock_user_update):
        mock_user_repository.get_by_id.return_value = mock_user
        mock_user_repository.get_by_email_or_username.return_value = mock_user

        with pytest.raises(EmailOrUsernameAlreadyExists):
            await user_service.update_user_by_id(1, mock_user_update)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_user_successful(self, user_service, mock_user_repository, mock_user):
        mock_user_repository.get_by_id.return_value = mock_user

        await user_service.delete_user_by_id(1)

        mock_user_repository.delete.assert_called_once_with(mock_user)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_user_failed(self, user_service, mock_user_repository):
        mock_user_repository.get_by_id.return_value = None

        with pytest.raises(UserWithIdNotFound):
            await user_service.delete_user_by_id(1)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_username_successful(self, user_service, mock_user_repository, mock_user):
        mock_user_repository.get_by_username.return_value = mock_user

        result = await user_service.get_by_username("test")
        assert result.username == mock_user.username

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_username_failed(self, user_service, mock_user_repository):
        mock_user_repository.get_by_username.return_value = None

        with pytest.raises(UserWithUsernameNotFound):
            await user_service.get_by_username("test")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_email_successful(self, user_service, mock_user_repository, mock_user):
        mock_user_repository.get_by_email.return_value = mock_user

        result = await user_service.get_by_email("test@example.com")
        assert result.email == mock_user.email

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_email_failed(self, user_service, mock_user_repository):
        mock_user_repository.get_by_email.return_value = None

        with pytest.raises(UserWithEmailNotFound):
            await user_service.get_by_email("test@example.com")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_save_user_avatar_image_success(self, user_service, mock_user_repository, mock_user,
                                                  mock_image_service):
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "avatar.jpg"
        mock_user_repository.get_by_id.return_value = mock_user
        mock_image_service.save_user_avatar_image.return_value = "http://example.com/avatar.jpg"
        mock_user_repository.save_user_avatar.return_value = mock_user

        result = await user_service.save_user_avatar_image(mock_file, user_id=1)

        mock_image_service.save_user_avatar_image.assert_called_once()
        mock_user_repository.save_user_avatar.assert_called_once()
        assert result.id == mock_user.id