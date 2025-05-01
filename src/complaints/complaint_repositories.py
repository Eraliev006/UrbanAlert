from typing import Optional

from sqlalchemy import select, Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.common import DatabaseError
from src.complaints import ComplaintWithIdNotFound, AccessDenied
from src.complaints.models import ComplaintCreate, Complaint, ComplaintRead, ComplaintUpdate


class ComplaintService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_complaint(self, complaint: ComplaintCreate) -> Optional[ComplaintRead]:
        """
        Method that creates new complaint in DB
        :param complaint:
        """
        complaint_in_db = Complaint(
            **complaint.model_dump()
        )

        try:
            self.db.add(complaint_in_db)
            await self.db.commit()
            await self.db.refresh(complaint_in_db)

            return ComplaintRead(**complaint.model_dump())
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseError('Error while adding new complaint')


    async def get_all(self) -> Optional[list[ComplaintRead]]:
        try:
            stmt = select(Complaint)
            result: Result = await self.db.execute(stmt)
            complaints = result.scalars()
            return list(ComplaintRead(**i.model_dump()) for i in complaints)

        except SQLAlchemyError:
            raise DatabaseError('Error while getting all Complaints')


    async def _get_by_id(self, complaint_id: int) -> Optional[Complaint]:
        try:
            complaint = await self.db.get(Complaint, complaint_id)
            if not complaint:
                raise ComplaintWithIdNotFound(complaint_id)

        except SQLAlchemyError:
            raise DatabaseError('Error while getting user with id')


    async def get_by_id(self, complaint_id: int) -> ComplaintRead:
        complaint = await self._get_by_id(complaint_id)
        return ComplaintRead(**complaint.model_dump())


    async def update_complaint(self, complaint_id: int, user_id: int, new_data: ComplaintUpdate) -> ComplaintRead:
        complaint = await self._get_by_id(complaint_id)

        if user_id != complaint.user_id:
            raise AccessDenied

        for key, value in new_data.model_dump().items():
            setattr(complaint, key, value)

        try:
            await self.db.commit()
            await self.db.refresh(complaint)
            return ComplaintRead(**complaint.model_dump())
        except SQLAlchemyError:
            raise DatabaseError('database error while updating complaint')


    async def delete_by_id(self, complaint_id: int, user_id: int) -> None:
        complaint = await self._get_by_id(complaint_id)

        if complaint.user_id != user_id:
            raise AccessDenied

        try:
            await self.db.delete(complaint)
            await self.db.commit()
        except SQLAlchemyError:
            raise DatabaseError("Database error while deleting complaint")
