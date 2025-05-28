import datetime
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from src import Complaint, Comment, ComplaintStatus
from src.complaints import ComplaintService, ComplaintCreate, ComplaintUpdate
from src.complaints.repositories import ComplaintRepositories
from test.unit.user.fixtures import user

@pytest_asyncio.fixture
def complaint_repository(session):
    return ComplaintRepositories(session)

@pytest_asyncio.fixture(scope='function')
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

@pytest_asyncio.fixture(scope='function')
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

@pytest_asyncio.fixture(scope='function')
async def mock_complaint_repository():
    repository = AsyncMock()
    return repository

@pytest_asyncio.fixture(scope='function')
async def mock_user_service():
    service = AsyncMock()
    return service


@pytest_asyncio.fixture()
async def complaint_service(mock_user_service, mock_image_service, mock_complaint_repository) -> ComplaintService:
    return ComplaintService(
        user_service=mock_user_service,
        complaint_repo=mock_complaint_repository,
        image_service=mock_image_service
    )

@pytest.fixture()
def mock_complaint():
    return Complaint(
        id = 1,
        complaint_text = 'some complaint',
        category = 'road problem',
        latitude = 0.000,
        longitude = 1.000,
        description = 'complaint description',
        status = ComplaintStatus.PENDING,
        image_url = '',
        user_id = 1,
        created_at = datetime.date.today(),
        updated_at = datetime.date.today(),
    )

@pytest_asyncio.fixture()
def mock_complaint_create():
    return ComplaintCreate(
        complaint_text='some complaint',
        category='road problem',
        latitude=0.000,
        longitude=1.000,
        description='complaint description',
        status=ComplaintStatus.PENDING,
    )
@pytest_asyncio.fixture()
def mock_complaint_update():
    return ComplaintUpdate(
        status = ComplaintStatus.APPROVED
    )