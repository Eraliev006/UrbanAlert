import pytest

from src.common import DatabaseError
from src.users import UserUpdate
from test import random_lower_string, random_email
from test.unit.user.fixtures import user_repository, fake_user, user


class TestUserRepository:
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create(self, user_repository, fake_user):
        created_user = await user_repository.create(fake_user)
        assert created_user.id is not None
        assert created_user.username == fake_user.username

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_integrity_error(self, user_repository, fake_user,user):
        with pytest.raises(DatabaseError):
            await user_repository.create(fake_user)


    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_id(self, user_repository, user):
        exists_user = await user_repository.get_by_id(user_id=user.id)

        assert exists_user
        assert exists_user is not None


    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_username(self, user_repository, fake_user, user):
        exists = await user_repository.get_by_username(user.username)
        assert exists.username == fake_user.username

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_email(self, user_repository, fake_user, user):
        exists = await user_repository.get_by_email(user.email)
        assert exists.email == fake_user.email

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update(self, user_repository, user):
        new_data = UserUpdate(
            username=random_lower_string(),
            email=random_email(),
        )
        updated = await user_repository.update(
            user = user,
            new_data = new_data
        )

        assert updated.email == new_data.email
        assert updated.username == new_data.username


    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete(self, user_repository, user):
        await user_repository.delete(user)
        assert await user_repository.get_by_id(user_id=user.id) is None


    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_set_verified(self, user_repository, user):
        await user_repository.set_verified(user)
        assert user.is_verified

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_save_image(self, user, user_repository):
        await user_repository.save_user_avatar(
            avatar_url='some_url',
            user_id = user.id
        )
        assert user.avatar_url
