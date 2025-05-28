from unittest import mock

import pytest

from src.complaints import ComplaintWithIdNotFound, AccessDenied


class TestComplaintService:

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create(self, complaint_service, mock_complaint_repository, mock_complaint, mock_complaint_create):
        mock_complaint_repository.create.return_value = mock_complaint

        result = await complaint_service.create_complaint(mock_complaint_create, 1)

        mock_complaint_repository.create.assert_called_once_with(mock.ANY)
        assert result.id == mock_complaint.id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_id_successful(self, complaint_service, mock_complaint_repository, mock_complaint):
        complaint_id = 1
        mock_complaint_repository.get_by_id_with_comments.return_value = mock_complaint

        result = await complaint_service.get_by_id(complaint_id)

        mock_complaint_repository.get_by_id_with_comments.assert_called_once_with(complaint_id)

        assert result.id == mock_complaint.id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_id_failed_not_found(self, complaint_service, mock_complaint_repository, mock_complaint):
        complaint_id = 1
        mock_complaint_repository.get_by_id_with_comments.return_value = None

        with pytest.raises(ComplaintWithIdNotFound):
            await complaint_service.get_by_id(complaint_id)

        mock_complaint_repository.get_by_id_with_comments.assert_called_once_with(complaint_id)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_complaint_successful(self, complaint_service, mock_complaint_repository, mock_complaint, mock_complaint_update):
        mock_complaint_repository.get_by_id.return_value = mock_complaint
        updated_mock = mock_complaint.model_copy(update={"status": mock_complaint_update.status})
        mock_complaint_repository.update.return_value = updated_mock
        old_status = mock_complaint.status

        complaint_id = 1
        user_id = 1
        result = await complaint_service.update_complaint(complaint_id, user_id, mock_complaint_update)

        mock_complaint_repository.get_by_id.assert_called_once_with(complaint_id)
        mock_complaint_repository.update.assert_called_once_with(
            complaint=mock_complaint,
            new_data=mock_complaint_update
        )
        assert result
        assert old_status != result.status


    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_complaint_failed_not_found(self, complaint_service, mock_complaint_repository, mock_complaint):
        mock_complaint_repository.get_by_id.return_value = None
        complaint_id = 1
        user_id = 1

        with pytest.raises(ComplaintWithIdNotFound):
            await complaint_service.update_complaint(complaint_id, user_id, mock_complaint)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_complaint_failed_access_denied(self, complaint_service, mock_complaint_repository,
                                                     mock_complaint):
        mock_complaint_repository.get_by_id.return_value = mock_complaint
        complaint_id = 1
        user_id = 2

        with pytest.raises(AccessDenied):
            await complaint_service.update_complaint(complaint_id, user_id, mock_complaint)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_complaint_successful(self, complaint_service, mock_complaint_repository,
                                                     mock_complaint):
        mock_complaint_repository.get_by_id.return_value = mock_complaint
        mock_complaint_repository.delete.return_value = None
        complaint_id = 1
        user_id = 1

        result = await complaint_service.delete_by_id(complaint_id, user_id)

        mock_complaint_repository.get_by_id.assert_called_once_with(complaint_id)
        mock_complaint_repository.delete.assert_called_once_with(mock_complaint)

        assert result is None

    async def test_get_complaints_by_user_id(self, complaint_service, mock_complaint_repository, mock_complaint,
                                             mock_user_service):
        user_id = 1
        mock_user_service.get_user_by_id.return_value = mock.Mock()
        mock_complaint_repository.get_by_user_id.return_value = [mock_complaint]

        result = await complaint_service.get_complaints_by_user_id(user_id)

        mock_user_service.get_user_by_id.assert_called_once_with(user_id)
        mock_complaint_repository.get_by_user_id.assert_called_once_with(user_id)
        assert isinstance(result, list)
        assert result[0].id == mock_complaint.id