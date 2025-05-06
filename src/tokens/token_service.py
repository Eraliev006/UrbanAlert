import datetime
from datetime import timedelta, timezone
from typing import Any

import jwt
from jwt import InvalidSignatureError, ExpiredSignatureError
from src.core import settings
from src.core.redis_client import RedisClient
from .exceptions import InvalidTokenType, InvalidSignatureException, ExpiredTokenSignatureException, DecodeTokenError, RefreshTokenNotFound
from src.tokens.token_type import TokenType
from src.users.models import User
from src.users import UserRead


class TokenService:
    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client

    async def save_refresh_token(self,user_id:int, token:str):
        await self.redis_client.set(f'refresh_token:{user_id}', token, ex=timedelta(days=30))

    async def verify_refresh_token(self, user_id: int, provided_token: str) -> None:
        stored_token = await self.redis_client.get(f'refresh_token:{user_id}')
        if not stored_token:
            raise RefreshTokenNotFound

        if stored_token != provided_token:
            raise InvalidSignatureException


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

    def get_access_and_refresh_tokens(self, user: User | UserRead):
        access_token = self.create_access_token(
            user_id=user.id,
            username=user.username,
            email=str(user.email),
            avatar_url=user.avatar_url,
            is_verified=user.is_verified
        )
        refresh_token = self.create_refresh_token(
            user_id=user.id,
            username=user.username,
        )
        return access_token, refresh_token

    @staticmethod
    def decode_token_with_token_type_checking(
            token: str,
            token_type: TokenType,
            algorithm: str = settings.jwt.algorithm,
            secret_key=settings.jwt.secret_key
    ):
        try:
            decoded = jwt.decode(
                jwt=token,
                algorithms=[algorithm],
                key=secret_key,
            )
            if decoded['type'] != token_type.value:
                raise InvalidTokenType

            return decoded
        except InvalidSignatureError:
            raise InvalidSignatureException

        except ExpiredSignatureError:
            raise ExpiredTokenSignatureException

        except jwt.DecodeError:
            raise DecodeTokenError