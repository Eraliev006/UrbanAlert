import logging
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel import and_

from .schemas import ComplaintUpdate, ComplaintQueryModel
from .models import Complaint
from src.common import BaseRepository, db_exception_handler


# Настройка логгера
logger = logging.getLogger('fixkg.complaint_repository')
logger.setLevel(logging.DEBUG)

class ComplaintRepositories(BaseRepository):
    @db_exception_handler
    async def create(self, complaint: Complaint) -> Complaint:
        logger.debug('Создание жалобы: %s', complaint)
        self.db.add(complaint)
        await self.db.commit()
        await self.db.refresh(complaint)
        logger.info('Жалоба успешно создана с ID: %d', complaint.id)

        return complaint

    @db_exception_handler
    async def get_all(self, query_param: ComplaintQueryModel) -> list[Complaint]:
        logger.debug('Получение всех жалоб с параметрами: %s', query_param)
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
        logger.info('Найдено %d жалоб', len(list(results)))

        return list(results)

    @db_exception_handler
    async def get_by_id(self, complaint_id: int) -> Complaint:
        logger.debug('Получение жалобы по ID: %d', complaint_id)
        stmt = select(Complaint).where(Complaint.id == complaint_id)
        complaint = await self.db.scalar(stmt)

        if not complaint:
            logger.error('Жалоба с ID %d не найдена', complaint_id)

        return complaint

    async def get_by_id_with_comments(self, complaint_id: int) -> Complaint:
        logger.debug('Получение жалобы с комментариями по ID: %d', complaint_id)
        stmt = (
            select(Complaint)
            .where(Complaint.id == complaint_id)
            .options(selectinload(Complaint.comments))
        )
        result = await self.db.execute(stmt)
        complaint = result.scalars().first()

        if not complaint:
            logger.error('Жалоба с ID %d не найдена', complaint_id)

        return complaint

    @db_exception_handler
    async def update(self, complaint: Complaint, new_data: ComplaintUpdate) -> Complaint:
        logger.debug('Обновление жалобы с ID: %d новыми данными: %s', complaint.id, new_data)
        updated_instance = await self.update_instance(
            instance=complaint,
            new_data=new_data
        )
        logger.info('Жалоба с ID %d успешно обновлена', complaint.id)

        return updated_instance

    @db_exception_handler
    async def delete(self, complaint: Complaint):
        logger.debug('Удаление жалобы с ID: %d', complaint.id)
        await self.db.delete(complaint)
        await self.db.commit()
        logger.info('Жалоба с ID %d успешно удалена', complaint.id)

        return None

    @db_exception_handler
    async def get_by_user_id(self, user_id: int) -> list[Complaint]:
        logger.debug('Получение жалоб пользователя с ID: %d', user_id)
        stmt = select(Complaint).where(Complaint.user_id == user_id)
        complaints = await self.db.scalars(stmt)

        logger.info('Найдено %d жалоб для пользователя с ID: %d', len(complaints), user_id)

        return list(complaints)

    @db_exception_handler
    async def save_complaint_image(self, complaint_id: int, image_url: str):
        logger.debug('Сохранение изображения для жалобы с ID: %d', complaint_id)
        complaint = await self.get_by_id(complaint_id)
        complaint.image_url = image_url
        await self.db.commit()
        await self.db.refresh(complaint)
        logger.info('Изображение для жалобы с ID %d обновлено с URL: %s', complaint_id, image_url)

        return complaint
