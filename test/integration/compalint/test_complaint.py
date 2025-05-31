import pytest

from src import ComplaintStatus
from src.main import app
from src.core import get_current_user
from src.complaints import ComplaintUpdate


class TestComplaint:
    base_url = "/complaints/"

    @pytest.mark.asyncio
    async def test_create_complaint(self, async_client, session, mock_user, mock_complaint_create):
        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = await async_client.post(self.base_url, json=mock_complaint_create.model_dump())
        assert response.status_code == 200
        data = response.json()
        assert data["complaint_text"] == mock_complaint_create.complaint_text
        assert data["user_id"] == mock_user.id

        app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_get_all_complaints(self, async_client, mock_user, session, mock_complaint):
        session.add(mock_complaint)
        await session.commit()

        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = await async_client.get(self.base_url, params={})
        assert response.status_code == 200
        assert isinstance(response.json(), list)

        app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_get_complaint_by_id(self, async_client, mock_user, session, mock_complaint):
        session.add(mock_complaint)
        await session.commit()

        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = await async_client.get(f"{self.base_url}{mock_complaint.id}")
        assert response.status_code == 200
        assert response.json()["id"] == mock_complaint.id

        app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_update_complaint(self, async_client, mock_user, session, mock_complaint):
        session.add(mock_complaint)
        await session.commit()

        app.dependency_overrides[get_current_user] = lambda: mock_user

        update_data = ComplaintUpdate(status=ComplaintStatus.APPROVED)
        response = await async_client.patch(
            f"{self.base_url}{mock_complaint.id}", json=update_data.model_dump(exclude_unset=True)
        )

        assert response.status_code == 200
        assert response.json()["status"] == update_data.status

        app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_delete_complaint(self, async_client, mock_user, session, mock_complaint):
        session.add(mock_complaint)
        await session.commit()

        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = await async_client.delete(f"{self.base_url}{mock_complaint.id}")
        assert response.status_code == 200
        assert response.json() is None

        app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_get_statuses(self, async_client, mock_user):
        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = await async_client.get(f"{self.base_url}statuses")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

        app.dependency_overrides = {}
