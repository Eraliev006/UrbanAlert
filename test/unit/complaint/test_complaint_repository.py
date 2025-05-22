import pytest

from src import Complaint, ComplaintStatus, Comment
from src.complaints import ComplaintUpdate
from test.unit.complaint.complaint_fixtures import complaint_repository, fake_complaint, complaint_with_user_and_comments

class TestComplaintRepository:
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create(self, complaint_repository, fake_complaint):
        created = await complaint_repository.create(fake_complaint)

        assert created.id
        assert isinstance(created, Complaint)
        assert created.user_id == fake_complaint.user_id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_id(self, complaint_repository, fake_complaint):
        complaint = await complaint_repository.get_by_id(fake_complaint.id)

        assert complaint

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_id_with_comments(self, complaint_with_user_and_comments, complaint_repository, fake_complaint):
        complaint = await complaint_repository.get_by_id_with_comments(complaint_with_user_and_comments.id)
        assert len(complaint.comments) == 3
        assert all(isinstance(c, Comment) for c in complaint.comments)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update(self, fake_complaint, complaint_repository):
        old_status = fake_complaint.status
        new_data = ComplaintUpdate(
            status = ComplaintStatus.CLOSED
        )
        updated = await complaint_repository.update(
            complaint=fake_complaint,
            new_data=new_data
        )

        assert updated.status != old_status

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete(self, fake_complaint, complaint_repository):
        await complaint_repository.delete(fake_complaint)
        assert await complaint_repository.get_by_id(complaint_id=fake_complaint.id) is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_user_id(self, fake_complaint, complaint_repository, user):
        complaints = await complaint_repository.get_by_user_id(user.id)
        assert len(complaints) != 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_save_image(self, fake_complaint, complaint_repository):
        await complaint_repository.save_complaint_image(
            image_url='some_url',
            complaint_id = fake_complaint.id
        )
        assert fake_complaint.image_url