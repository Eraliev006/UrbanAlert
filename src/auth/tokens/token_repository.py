from datetime import timedelta
from typing import Optional

from src.core.redis_client import RedisClient


class TokenRepository:
    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client

    async def save_refresh_token(self,user_id:int, token:str):
        await self.redis_client.set(f'refresh_token:{user_id}', token, ex=timedelta(days=30))

    async def get_refresh_token(self, user_id: int) -> Optional[str]:
        return await self.redis_client.get(f'refresh_token:{user_id}')

    async def delete_refresh_token(self, user_id: int):
        await self.redis_client.delete(f'refresh_token:{user_id}')
