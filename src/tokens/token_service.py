import datetime
from datetime import timedelta, timezone, datetime
from typing import Optional, Any

import jwt
from jwt import InvalidSignatureError, ExpiredSignatureError

from src.auth import InvalidSignatureException
from src.auth.exceptions import ExpiredTokenSignatureException
from src.core import settings
from src.core.redis_client import RedisClient
from src.tokens import TokenType


class TokenService:
    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client

    async def save_refresh_token(self,user_id:int, token:str):
        await self.redis_client.set(f'refresh_token:{user_id}', token, ex=timedelta(days=30))

    async def get_refresh_token(self, user_id: int) -> Optional[str]:
        return await self.redis_client.get(f'refresh_token:{user_id}')

    async def delete_refresh_token(self, user_id: int):
        await self.redis_client.delete(f'refresh_token:{user_id}')

    @staticmethod
    def get_token_expiration(time_minutes) -> datetime:
        return datetime.datetime.now(tz=timezone.utc) + timedelta(minutes=time_minutes)

    def _build_token(
            self,
            payload: dict[str, Any],
            expire_in_minutes: int,
            token_type: TokenType,
            secret_key: str = settings.jwt.secret_key,
            algorithm: str = settings.jwt.algorithm,
    ) -> str:
        token_payload = {
            **payload,
            'type': token_type.value,
            'exp': self.get_token_expiration(expire_in_minutes)
        }
        return jwt.encode(
            payload=token_payload,
            key=secret_key,
            algorithm=algorithm
        )

    def create_access_token(self, user_id: int, email: str, username: str, avatar_url: str, is_verified: bool) -> str:
        payload = {
            'sub': str(user_id),
            'email': email,
            'username': username,
            'avatar_url': avatar_url,
            'is_verified': is_verified
        }
        return self._build_token(
            payload=payload,
            expire_in_minutes=settings.jwt.access_expires_in_minutes,
            token_type=TokenType.access
        )

    def create_refresh_token(self, user_id: int, username: str) -> str:
        payload = {
            'sub': str(user_id),
            'username': username,
        }
        return self._build_token(
            payload=payload,
            expire_in_minutes=settings.jwt.refresh_expires_in_minutes,
            token_type=TokenType.refresh
        )

    @staticmethod
    def decode_token(
            token: str,
            algorithm: str = settings.jwt.algorithm,
            secret_key=settings.jwt.secret_key
    ):
        try:
            return jwt.decode(
                jwt=token,
                algorithms=[algorithm],
                key=secret_key,
            )

        except InvalidSignatureError:
            raise InvalidSignatureException

        except ExpiredSignatureError:
            raise ExpiredTokenSignatureException