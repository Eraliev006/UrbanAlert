import pytest

from test.unit.comments.comment_fixtures import comment_repository, fake_comment, fake_comment_data

class TestCommentRepositories:

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_comment(self, comment_repository, fake_comment_data):
        created = await comment_repository.create(fake_comment_data)
        assert created

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_id(self, comment_repository, fake_comment):
        created = await comment_repository.get_by_id(fake_comment.id)
        assert created

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete(self, comment_repository, fake_comment):
        await comment_repository.delete(fake_comment)
        deleted = await comment_repository.get_by_id(fake_comment.id)
        assert deleted is None