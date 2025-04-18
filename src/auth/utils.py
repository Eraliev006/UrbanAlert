import datetime
import enum
from datetime import timezone, timedelta
from typing import Any

import jwt
from jwt import InvalidSignatureError, ExpiredSignatureError

from src.auth import TokenPairs
from src.auth.exceptions import ExpiredTokenSignatureException, InvalidSignatureException
from src.core import settings

class TokenType(enum.Enum):
    refresh = 'refresh'
    access = 'access'

def _create_token(
        payload: dict[str, Any],
        private_key: str,
        algorithm: str,
        token_type: TokenType,
        access_expire_in_minutes: int = settings.jwt.access_expires_in_minutes,
        refresh_expire_in_minutes: int = settings.jwt.refresh_expires_in_minutes,
) -> str:
    expire_minutes = (
        refresh_expire_in_minutes if token_type == TokenType.refresh else access_expire_in_minutes
    )

    exp = datetime.datetime.now(tz=timezone.utc) + timedelta(minutes=expire_minutes)
    return jwt.encode(
        payload={
            **payload,
            'type': token_type.value,
            'exp': exp
        },
        key=private_key,
        algorithm=algorithm
    )

def create_tokens(
        payload: dict[str, Any],
        private_key_path: str = settings.jwt.private_key,
        algorithm: str = settings.jwt.algorithm,
        access_expire_in_minutes: int = settings.jwt.access_expires_in_minutes,
        refresh_expire_in_minutes: int = settings.jwt.refresh_expires_in_minutes,
) -> TokenPairs:

    with open(private_key_path, 'r') as f:
        private_key = f.read()

        access_token = _create_token(payload, private_key, algorithm, TokenType.access, access_expire_in_minutes)
        refresh_token = _create_token(payload, private_key, algorithm, TokenType.refresh, refresh_expire_in_minutes)

    return TokenPairs(
        access_token = access_token,
        refresh_token = refresh_token
    )

def decode_token(
        token: str,
        algorithm: str = settings.jwt.algorithm,
        public_key_path: str = settings.jwt.public_key,
):
    with open(public_key_path, 'r') as f:
        public_key = f.read()
        try:

            return jwt.decode(
                jwt = token,
                algorithms=[algorithm],
                key=public_key,
            )

        except InvalidSignatureError:
            raise InvalidSignatureException

        except ExpiredSignatureError:
            raise ExpiredTokenSignatureException

