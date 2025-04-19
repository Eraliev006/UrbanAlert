from typing import Any

import jwt
from jwt import InvalidSignatureError, ExpiredSignatureError

from src.auth import TokenPairs
from src.auth.exceptions import ExpiredTokenSignatureException, InvalidSignatureException
from src.auth.tokens.access import AccessTokenCreator
from src.auth.tokens.refresh import RefreshTokenCreator
from src.core import settings


def get_pairs_token(payload: dict[str, Any]) -> TokenPairs:
    access_token = AccessTokenCreator().generate(payload)
    refresh_token = RefreshTokenCreator().generate(payload)

    return TokenPairs(
        access_token = access_token,
        refresh_token = refresh_token
    )

def decode_token(
        token: str,
        algorithm: str = settings.jwt.algorithm,
        secret_key = settings.jwt.secret_key
):
    try:
        return jwt.decode(
            jwt = token,
            algorithms=[algorithm],
            key=secret_key,
        )

    except InvalidSignatureError:
        raise InvalidSignatureException

    except ExpiredSignatureError:
        raise ExpiredTokenSignatureException

def hash_password(password: bytes) -> str:
    """Hash password"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    return pwd_context.hash(password)

def verify_password(plain_pass: bytes, hashed_password: bytes) -> bool:
    """Verify password"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    return pwd_context.verify(plain_pass, hashed_password)