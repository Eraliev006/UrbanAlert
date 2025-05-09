from fastapi import UploadFile

from .exceptions import ComplaintWithIdNotFound, AccessDenied
from .schemas import ComplaintCreate, ComplaintRead, ComplaintUpdate, ComplaintQueryModel, ComplaintReadDetailsSchemas
from src.complaints import Complaint

from src.complaints.repositories import ComplaintRepositories
from src.comments.schemas import CommentRead
from src.users import UserService
from src.images import ImageService


class ComplaintService:
    def __init__(self, complaint_repo: ComplaintRepositories,user_service: UserService, image_service: ImageService):
        self._complaint_repo = complaint_repo
        self._user_service = user_service
        self._image_service = image_service

    @staticmethod
    def _ensure_user_access(complaint_user_id: int, user_id: int) -> None:
        if complaint_user_id != user_id:
            raise AccessDenied

    async def create_complaint(self, complaint: ComplaintCreate, user_id: int) -> ComplaintRead | None:
        """
        Method that creates new complaint in DB
        :param complaint:
        :param user_id:
        """
        complaint_in_db = Complaint(
            **complaint.model_dump(),
            user_id = user_id
        )
        created = await self._complaint_repo.create(complaint_in_db)
        return ComplaintRead(**created.model_dump())


    async def get_all(self, query_params: ComplaintQueryModel) -> list[ComplaintRead]:
        complaints = await self._complaint_repo.get_all(query_params)
        return [ComplaintRead(**complaint.model_dump()) for complaint in complaints]


    async def get_by_id(self, complaint_id: int) -> ComplaintReadDetailsSchemas:
        complaint = await self._complaint_repo.get_by_id_with_comments(complaint_id)

        if not complaint:
            raise ComplaintWithIdNotFound(complaint_id)

        return ComplaintReadDetailsSchemas(**complaint.model_dump(),comments=[CommentRead(**c.model_dump()) for c in complaint.comments]

)


    async def update_complaint(self, complaint_id: int, user_id: int, new_data: ComplaintUpdate) -> ComplaintRead:
        complaint = await self._complaint_repo.get_by_id(complaint_id)

        if not complaint:
            raise ComplaintWithIdNotFound(complaint_id)

        self._ensure_user_access(complaint.user_id, user_id)

        updated = await self._complaint_repo.update(
            complaint=complaint,
            new_data=new_data,
        )
        return ComplaintRead(**updated.model_dump())

    async def delete_by_id(self, complaint_id: int, user_id: int) -> None:
        complaint = await self._complaint_repo.get_by_id(complaint_id)

        if not complaint:
            raise ComplaintWithIdNotFound(complaint_id)

        self._ensure_user_access(complaint.user_id, user_id)

        await self._complaint_repo.delete(complaint)

    async def get_complaints_by_user_id(self, user_id: int) -> list[ComplaintRead]:
        await self._user_service.get_user_by_id(user_id)

        complaints = await self._complaint_repo.get_by_user_id(user_id)

        return [ComplaintRead(**complaint.model_dump()) for complaint in complaints]

    async def upload_complaint_image(self, file: UploadFile, complaint_id: int) -> ComplaintRead:
        await self.get_by_id(complaint_id)

        image_url = await self._image_service.save_complaint_image(file, complaint_id)

        updated_complaint = await self._complaint_repo.save_complaint_image(
            image_url=image_url,
            complaint_id=complaint_id
        )

        return ComplaintRead(**updated_complaint.model_dump())
