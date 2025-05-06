from sqlalchemy.orm import selectinload
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
        filters = []

        if query_param.status:
            filters.append(Complaint.status == query_param.status)

        if query_param.category:
            filters.append(Complaint.category == query_param.category)

        stmt = select(Complaint)

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.limit(query_param.limit).offset(query_param.offset)

        results = await self.db.scalars(stmt)
        return list(results)


    @db_exception_handler
    async def get_by_id(self, complaint_id: int) -> Complaint:
        stmt = select(Complaint).where(Complaint.id == complaint_id)
        complaint = await self.db.scalar(stmt)

        return complaint

    async def get_by_id_with_comments(self, complaint_id: int) -> Complaint:
        stmt = (
            select(Complaint)
            .where(Complaint.id == complaint_id)
            .options(selectinload(Complaint.comments))
        )
        result = await self.db.execute(stmt)
        complaint = result.scalars().first()
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
