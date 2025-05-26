import pytest

from src import Comment
from src.comments import CommentRepositories

@pytest.fixture(scope='function')
def comment_repository(session):
    return CommentRepositories(session)

@pytest.fixture(scope='function')
def fake_comment_data(fake_complaint, user):
    comment = Comment(
        user_id = user.id,
        complaint_id = fake_complaint.id,
        content = 'Some comment'
    )
    return comment

@pytest.fixture(scope='function')
async def fake_comment(comment_repository, fake_complaint, user):
    comment = Comment(
        user_id = user.id,
        complaint_id = fake_complaint.id,
        content = 'Some comment'
    )
    return await comment_repository.create(comment)