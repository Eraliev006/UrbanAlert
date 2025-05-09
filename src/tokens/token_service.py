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
import logging

logger = logging.getLogger('fixkg.token_service')


class TokenService:
    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client
        logger.info('TokenService initialized with Redis client')

    async def save_refresh_token(self, user_id: int, token: str):
        logger.debug('Saving refresh token for user_id=%d', user_id)
        await self.redis_client.set(f'refresh_token:{user_id}', token, ex=timedelta(days=30))
        logger.info('Refresh token saved for user_id=%d', user_id)

    async def verify_refresh_token(self, user_id: int, provided_token: str) -> None:
        logger.debug('Verifying refresh token for user_id=%d', user_id)
        stored_token = await self.redis_client.get(f'refresh_token:{user_id}')
        if not stored_token:
            logger.error('Refresh token not found for user_id=%d', user_id)
            raise RefreshTokenNotFound

        if stored_token != provided_token:
            logger.error('Invalid refresh token for user_id=%d', user_id)
            raise InvalidSignatureException
        logger.info('Refresh token verified for user_id=%d', user_id)

    async def delete_refresh_token(self, user_id: int):
        logger.debug('Deleting refresh token for user_id=%d', user_id)
        await self.redis_client.delete(f'refresh_token:{user_id}')
        logger.info('Refresh token deleted for user_id=%d', user_id)

    @staticmethod
    def get_token_expiration(time_minutes) -> datetime:
        expiration = datetime.datetime.now(tz=timezone.utc) + timedelta(minutes=time_minutes)
        logger.debug('Token expiration time: %s', expiration)
        return expiration

    def _build_token(
            self,
            payload: dict[str, Any],
            expire_in_minutes: int,
            token_type: TokenType,
            secret_key: str = settings.jwt.secret_key,
            algorithm: str = settings.jwt.algorithm,
    ) -> str:
        logger.debug('Building token with payload: %s', payload)
        token_payload = {
            **payload,
            'type': token_type.value,
            'exp': self.get_token_expiration(expire_in_minutes)
        }
        token = jwt.encode(
            payload=token_payload,
            key=secret_key,
            algorithm=algorithm
        )
        logger.debug('Token created successfully')
        return token

    def create_access_token(self, user_id: int, email: str, username: str, avatar_url: str, is_verified: bool) -> str:
        logger.debug('Creating access token for user_id=%d', user_id)
        payload = {
            'sub': str(user_id),
            'email': email,
            'username': username,
            'avatar_url': avatar_url,
            'is_verified': is_verified
        }
        access_token = self._build_token(
            payload=payload,
            expire_in_minutes=settings.jwt.access_expires_in_minutes,
            token_type=TokenType.access
        )
        logger.info('Access token created for user_id=%d', user_id)
        return access_token

    def create_refresh_token(self, user_id: int, username: str) -> str:
        logger.debug('Creating refresh token for user_id=%d', user_id)
        payload = {
            'sub': str(user_id),
            'username': username,
        }
        refresh_token = self._build_token(
            payload=payload,
            expire_in_minutes=settings.jwt.refresh_expires_in_minutes,
            token_type=TokenType.refresh
        )
        logger.info('Refresh token created for user_id=%d', user_id)
        return refresh_token

    def get_access_and_refresh_tokens(self, user: User | UserRead):
        logger.debug('Generating access and refresh tokens for user_id=%d', user.id)
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
        logger.info('Access and refresh tokens generated for user_id=%d', user.id)
        return access_token, refresh_token

    @staticmethod
    def decode_token_with_token_type_checking(
            token: str,
            token_type: TokenType,
            algorithm: str = settings.jwt.algorithm,
            secret_key=settings.jwt.secret_key
    ) -> dict[str, Any]:
        logger.debug('Decoding token with token_type=%s', token_type)
        try:
            decoded = jwt.decode(
                jwt=token,
                algorithms=[algorithm],
                key=secret_key,
            )
            if decoded['type'] != token_type.value:
                logger.error('Invalid token type for token_type=%s', token_type)
                raise InvalidTokenType

            logger.info('Token decoded successfully for token_type=%s', token_type)
            return decoded
        except InvalidSignatureError:
            logger.error('Invalid signature for token')
            raise InvalidSignatureException

        except ExpiredSignatureError:
            logger.error('Expired signature for token')
            raise ExpiredTokenSignatureException

        except jwt.DecodeError:
            logger.error('Token decoding error')
            raise DecodeTokenError
