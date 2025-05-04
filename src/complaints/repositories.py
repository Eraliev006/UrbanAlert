from sqlmodel import select

from sqlmodel import and_

from .schemas import ComplaintUpdate, ComplaintQueryModel
from .models import Complaint
from src.common import BaseRepository, db_exception_handler


class ComplaintRepositories(BaseRepository):
    @db_exception_handler
    async def create(self, complaint: Complaint) -> Complaint:
        self.db.add(complaint)
        await self.db.commit()
        await self.db.refresh(complaint)

        return complaint

    @db_exception_handler
    async def get_all(self, query_param: ComplaintQueryModel) -> list[Complaint]:
        stmt = select(Complaint).where(and_(
            Complaint.status == query_param.status,
            Complaint.category == query_param.category
        )).limit(query_param.limit).offset(query_param.offset)
        complaints = await self.db.scalars(stmt)

        return list(complaints)

    @db_exception_handler
    async def get_by_id(self, complaint_id: int) -> Complaint:
        stmt = select(Complaint).where(Complaint.id == complaint_id)
        complaint = await self.db.scalar(stmt)

        return complaint

    @db_exception_handler
    async def update(self, complaint: Complaint, new_data: ComplaintUpdate) -> Complaint:
        updated_instance = await self.update_instance(
            instance=complaint,
            new_data=new_data
        )

        return updated_instance

    @db_exception_handler
    async def delete(self, complaint: Complaint):
        await self.db.delete(complaint)
        await self.db.commit()

        return None

    @db_exception_handler
    async def get_by_user_id(self, user_id: int) -> list[Complaint]:
        stmt = select(Complaint).where(Complaint.user_id == user_id)
        complaints = await self.db.scalars(stmt)

        return list(complaints)
