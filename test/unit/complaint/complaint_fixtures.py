import pytest

from src import Complaint, Comment
from src.complaints.repositories import ComplaintRepositories
from test.unit.user.fixtures import user

@pytest.fixture
def complaint_repository(session):
    return ComplaintRepositories(session)

@pytest.fixture(scope='function')
async def fake_complaint(user, complaint_repository):
    complaint = Complaint(
        complaint_text='complaint1',
        category='Дороги',
        longitude=31231.3123,
        latitude=3123.3123,
        description='complaint1 description',
        user_id=user.id
    )
    return await complaint_repository.create(complaint)

@pytest.fixture(scope='function')
async def complaint_with_user_and_comments(complaint_repository, user, fake_complaint, session):
    comments = [
        Comment(
            user_id=user.id,
            complaint_id=fake_complaint.id,
            content='comment 1'
        ),
        Comment(
            user_id=user.id,
            complaint_id=fake_complaint.id,
            content='comment 2'
        ),
        Comment(
            user_id=user.id,
            complaint_id=fake_complaint.id,
            content='comment 3'
        ),
    ]

    session.add_all(comments)
    await session.flush()
    await session.commit()

    await session.refresh(fake_complaint)

    return fake_complaint
