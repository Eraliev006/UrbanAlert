from sqlalchemy.ext.asyncio import AsyncSession

from .db_decorators import db_exception_handler


class BaseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    @db_exception_handler
    async def update_instance(self, instance, update_data):
        for key, value in update_data.model_dump().items():
            if value is not None:
                setattr(instance, key, value)

        await self.db.commit()
        await self.db.refresh(instance)
        return instance