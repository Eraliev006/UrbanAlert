import pytest

from src.core import get_current_user
from src.main import app
from src.users import UserUpdate


class TestUser:
    base_url = '/users/'
    @pytest.mark.asyncio
    async def test_get_current_user_route(self, async_client, session,mock_user):
        session.add(mock_user)
        await session.commit()
        await session.refresh(mock_user)


        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = await async_client.get(f"{self.base_url}me")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"

        app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_get_all_users_route(self, async_client, mock_users_list, session, mock_user):
        session.add_all(mock_users_list)
        await session.commit()

        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = await async_client.get(f"{self.base_url}")
        assert response.status_code == 200
        users = response.json()
        assert len(users) >= 2
        emails = [u["email"] for u in users]
        assert mock_users_list[0].email in emails and mock_users_list[1].email in emails

        app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_update_user_route(self, async_client, mock_user, session):
        session.add(mock_user)
        await session.commit()

        app.dependency_overrides[get_current_user] = lambda: mock_user

        update_data = UserUpdate(username = 'new username')
        response = await async_client.patch(f"{self.base_url}me", json=update_data.model_dump())

        assert response.status_code == 202
        data = response.json()
        assert data["username"] == update_data.username

        app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_delete_user_route(self, async_client, mock_user, session):
        session.add(mock_user)
        await session.commit()

        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = await async_client.delete(f"{self.base_url}me")

        assert response.status_code == 204

        app.dependency_overrides = {}


    @pytest.mark.asyncio
    async def test_get_user_by_id(self, async_client, mock_user, session):
        session.add(mock_user)
        await session.commit()

        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = await async_client.get(f"{self.base_url}{mock_user.id}")

        assert response.status_code == 200
        assert response.json()
        assert response.json()['id']

        app.dependency_overrides = {}
