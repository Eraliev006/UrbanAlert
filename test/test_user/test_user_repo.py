from unittest.mock import MagicMock

import pytest

from src import User
from src.common import DatabaseError
from src.users import UserRepositories


class TestUserRepository:
    @staticmethod
    @pytest.mark.asyncio
    async def test_user_create(user_repository: UserRepositories, fake_user_data: User):
        created = await user_repository.create(fake_user_data)

        assert created.id is not None
        assert created.email == fake_user_data.email
        assert isinstance(created, User)

    @staticmethod
    @pytest.mark.asyncio
    async def test_user_create_failed(user_repository: UserRepositories, fake_user_data: User):
        fake_user_data.username = None
        with pytest.raises(DatabaseError):
            await user_repository.create(fake_user_data)

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_by_id(user_repository: UserRepositories, fake_user_data: User):
        created: User = await user_repository.create(fake_user_data)

        user = await user_repository.get_by_id(created.id)

        assert user
        assert isinstance(user, User)
        assert user.email

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_by_id_failed():
        db_mock = MagicMock()

        db_mock.scalar = MagicMock(side_effect=DatabaseError("SQL Error"))

        user_repository = UserRepositories(db_mock)

        with pytest.raises(DatabaseError):
            await user_repository.get_by_id(1)

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_all_users(user_repository: UserRepositories):
        users = await user_repository.get_all()

        assert type(users) is list


    @staticmethod
    @pytest.mark.asyncio
    async def test_get_by_username(user_repository: UserRepositories, fake_user_data: User):
        await user_repository.create(fake_user_data)

        user = await user_repository.get_by_username(fake_user_data.username)

        assert user
        assert isinstance(user, User)
        assert user.email

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_by_username_failed(user_repository_with_mock):
        with pytest.raises(DatabaseError):
            await user_repository_with_mock.get_by_username('error')

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_by_email(user_repository: UserRepositories, fake_user_data: User):
        await user_repository.create(fake_user_data)

        user = await user_repository.get_by_email(created = fake_user_data.email)

        assert user
        assert isinstance(user, User)
        assert user.username

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_by_email(user_repository_with_mock):
        with pytest.raises(DatabaseError):
            await user_repository_with_mock.get_by_email('error')

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_by_email_or_username(user_repository: UserRepositories, fake_user_data: User):
        await user_repository.create(fake_user_data)

        user_by_email = await user_repository.get_by_email_or_username(email=str(fake_user_data.email))
        user_by_username = await user_repository.get_by_email_or_username(username=fake_user_data.username)

        assert user_by_email is not None
        assert user_by_username is not None
        assert isinstance(user_by_email, User)
        assert isinstance(user_by_username, User)

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_by_email_or_username_failed(user_repository_with_mock):
        with pytest.raises(DatabaseError):
            await user_repository_with_mock.get_by_email_or_username(email="error@example.com")

    @staticmethod
    @pytest.mark.asyncio
    async def test_save_user_avatar(user_repository: UserRepositories, fake_user_data: User):
        created = await user_repository.create(fake_user_data)

        updated = await user_repository.save_user_avatar("http://example.com/avatar.jpg", created.id)

        assert updated.avatar_url == "http://example.com/avatar.jpg"

    @staticmethod
    @pytest.mark.asyncio
    async def test_set_verified(user_repository: UserRepositories, fake_user_data: User):
        created = await user_repository.create(fake_user_data)

        updated = await user_repository.set_verified(created, verified=True)

        assert updated.is_verified is True

    @staticmethod
    @pytest.mark.asyncio
    async def test_delete_user(user_repository: UserRepositories, fake_user_data: User):
        created = await user_repository.create(fake_user_data)
        await user_repository.delete(created)

        result = await user_repository.get_by_id(created.id)
        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_update_user(user_repository: UserRepositories, fake_user_data: User, fake_user_update_data):
        created = await user_repository.create(fake_user_data)


        updated = await user_repository.update(created, fake_user_update_data)

        assert updated.username == fake_user_data.username
        assert isinstance(updated, User)