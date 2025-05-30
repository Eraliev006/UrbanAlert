from datetime import timedelta

import redis.asyncio as redis

from src.core import settings


class RedisClient:

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, decode_responses: bool = True):
        self._client = None
        self.port = port
        self.host = host
        self.db = db
        self.decode_responses = decode_responses

    async def connect(self):
        self._client = redis.Redis(
            port = self.port,
            host = self.host,
            db = self.db,
            decode_responses = self.decode_responses
        )

    async def close(self):
        await self._client.aclose()

    def _get_client(self) -> redis.Redis:
        if not self._client:
            raise RuntimeError('Redis is not connected')
        return self._client

    async def set(self, key: str, value: str | int | dict | list | set, ex: int | timedelta = None):
        """
        :param: key: take a str and help to get data from redis by this key
        :param: value: a data
        :param: ex: take a life seconds
        """
        await self._get_client().set(name=key, value=value, ex=ex)

    async def get(self, key: str):
        return await self._get_client().get(name=key)

    async def delete(self, key: str):
        await self._get_client().delete(key)

redis_client = RedisClient(
    port = settings.redis.port,
    host = settings.redis.host,
    db=0,
    decode_responses=True
)
