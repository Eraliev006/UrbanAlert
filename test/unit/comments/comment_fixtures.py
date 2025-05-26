import pytest_asyncio

from src import Comment
from src.comments import CommentRepositories

@pytest_asyncio.fixture(scope='function')
def comment_repository(session):
    return CommentRepositories(session)

@pytest_asyncio.fixture(scope='function')
def fake_comment_data(fake_complaint, user):
    comment = Comment(
        user_id = user.id,
        complaint_id = fake_complaint.id,
        content = 'Some comment'
    )
    return comment

@pytest_asyncio.fixture(scope='function')
async def fake_comment(comment_repository, fake_complaint, user):
    comment = Comment(
        user_id = user.id,
        complaint_id = fake_complaint.id,
        content = 'Some comment'
    )
    return await comment_repository.create(comment)