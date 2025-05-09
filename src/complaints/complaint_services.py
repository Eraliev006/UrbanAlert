import logging
from fastapi import UploadFile

from .exceptions import ComplaintWithIdNotFound, AccessDenied
from .schemas import ComplaintCreate, ComplaintRead, ComplaintUpdate, ComplaintQueryModel, ComplaintReadDetailsSchemas
from src.complaints import Complaint
from src.complaints.repositories import ComplaintRepositories
from src.comments.schemas import CommentRead
from src.users import UserService
from src.images import ImageService


logger = logging.getLogger('fixkg.complaint_service')

class ComplaintService:
    def __init__(self, complaint_repo: ComplaintRepositories, user_service: UserService, image_service: ImageService):
        self._complaint_repo = complaint_repo
        self._user_service = user_service
        self._image_service = image_service
        logger.info('ComplaintService initialized')

    @staticmethod
    def _ensure_user_access(complaint_user_id: int, user_id: int) -> None:
        logger.debug('Checking access for user_id=%d to complaint_user_id=%d', user_id, complaint_user_id)
        if complaint_user_id != user_id:
            logger.error('Access denied for user_id=%d to complaint_user_id=%d', user_id, complaint_user_id)
            raise AccessDenied
        logger.debug('Access granted for user_id=%d to complaint_user_id=%d', user_id, complaint_user_id)

    async def create_complaint(self, complaint: ComplaintCreate, user_id: int) -> ComplaintRead | None:
        logger.debug('Creating complaint for user_id=%d', user_id)

        complaint_in_db = Complaint(
            **complaint.model_dump(),
            user_id=user_id
        )
        created = await self._complaint_repo.create(complaint_in_db)
        logger.info('Complaint created successfully for user_id=%d', user_id)

        return ComplaintRead(**created.model_dump())

    async def get_all(self, query_params: ComplaintQueryModel) -> list[ComplaintRead]:
        logger.debug('Fetching all complaints with query params: %s', query_params)
        complaints = await self._complaint_repo.get_all(query_params)
        logger.info('Fetched %d complaints', len(complaints))

        return [ComplaintRead(**complaint.model_dump()) for complaint in complaints]

    async def get_by_id(self, complaint_id: int) -> ComplaintReadDetailsSchemas:
        logger.debug('Fetching complaint by id=%d', complaint_id)
        complaint = await self._complaint_repo.get_by_id_with_comments(complaint_id)

        if not complaint:
            logger.error('Complaint with id=%d not found', complaint_id)
            raise ComplaintWithIdNotFound(complaint_id)

        logger.info('Complaint with id=%d found', complaint_id)
        return ComplaintReadDetailsSchemas(
            **complaint.model_dump(),
            comments=[CommentRead(**c.model_dump()) for c in complaint.comments]
        )

    async def update_complaint(self, complaint_id: int, user_id: int, new_data: ComplaintUpdate) -> ComplaintRead:
        logger.debug('Updating complaint with id=%d for user_id=%d', complaint_id, user_id)

        complaint = await self._complaint_repo.get_by_id(complaint_id)

        if not complaint:
            logger.error('Complaint with id=%d not found', complaint_id)
            raise ComplaintWithIdNotFound(complaint_id)

        self._ensure_user_access(complaint.user_id, user_id)

        updated = await self._complaint_repo.update(
            complaint=complaint,
            new_data=new_data,
        )
        logger.info('Complaint with id=%d updated successfully', complaint_id)
        return ComplaintRead(**updated.model_dump())

    async def delete_by_id(self, complaint_id: int, user_id: int) -> None:
        logger.debug('Deleting complaint with id=%d for user_id=%d', complaint_id, user_id)

        complaint = await self._complaint_repo.get_by_id(complaint_id)

        if not complaint:
            logger.error('Complaint with id=%d not found', complaint_id)
            raise ComplaintWithIdNotFound(complaint_id)

        self._ensure_user_access(complaint.user_id, user_id)

        await self._complaint_repo.delete(complaint)
        logger.info('Complaint with id=%d deleted successfully', complaint_id)

    async def get_complaints_by_user_id(self, user_id: int) -> list[ComplaintRead]:
        logger.debug('Fetching complaints for user_id=%d', user_id)

        await self._user_service.get_user_by_id(user_id)

        complaints = await self._complaint_repo.get_by_user_id(user_id)
        logger.info('Fetched %d complaints for user_id=%d', len(complaints), user_id)

        return [ComplaintRead(**complaint.model_dump()) for complaint in complaints]

    async def upload_complaint_image(self, file: UploadFile, complaint_id: int) -> ComplaintRead:
        logger.debug('Uploading image for complaint_id=%d', complaint_id)

        await self.get_by_id(complaint_id)

        image_url = await self._image_service.save_complaint_image(file, complaint_id)
        logger.info('Image uploaded successfully for complaint_id=%d', complaint_id)

        updated_complaint = await self._complaint_repo.save_complaint_image(
            image_url=image_url,
            complaint_id=complaint_id
        )
        logger.info('Complaint image updated for complaint_id=%d', complaint_id)

        return ComplaintRead(**updated_complaint.model_dump())
