import logging
from typing import Optional

from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import and_

from src.common import DatabaseError
from src.complaints import ComplaintWithIdNotFound, AccessDenied, ComplaintCreate, Complaint, ComplaintRead, \
    ComplaintUpdate, ComplaintQueryModel


class ComplaintService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_complaint(self, complaint: ComplaintCreate, user_id: int) -> Optional[ComplaintRead]:
        """
        Method that creates new complaint in DB
        :param complaint:
        :param user_id:
        """
        complaint_in_db = Complaint(
            **complaint.model_dump(),
            user_id = user_id
        )

        try:
            self.db.add(complaint_in_db)
            await self.db.commit()
            await self.db.refresh(complaint_in_db)

            return ComplaintRead(**complaint_in_db.model_dump())
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseError('Error while adding new complaint')


    async def get_all(self, query_params: Optional[ComplaintQueryModel]) -> Optional[list[ComplaintRead]]:
        try:
            stmt = select(Complaint).where(and_(
                Complaint.status == query_params.status,
                Complaint.category == query_params.category
            ))
            result = await self.db.scalars(stmt)
            return [ComplaintRead(**i.model_dump()) for i in result]

        except SQLAlchemyError as e:
            logging.exception('Exception ')
            raise e


    async def _get_by_id(self, complaint_id: int) -> Optional[Complaint]:
        try:
            complaint = await self.db.get(Complaint, complaint_id)
            if not complaint:
                raise ComplaintWithIdNotFound(complaint_id)

        except SQLAlchemyError as e:
            raise DatabaseError(f'Error while getting complaint with id {e}')


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

    async def get_complaints_by_user_id(self, user_id: int) -> list[ComplaintRead]:
        try:
            stmt = select(Complaint).where(Complaint.user_id == user_id)
            result = await self.db.scalars(stmt)
            complaints = result.all()
            return [ComplaintRead(**c.model_dump()) for c in complaints]
        except SQLAlchemyError:
            await self.db.rollback()
            raise DatabaseError('Error while fetching complaints for user')
