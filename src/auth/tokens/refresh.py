import datetime
from typing import Any

import jwt

from src.auth.tokens.base import TokenCreator
from src.auth.tokens.token_type import TokenType
from src.core import settings


class RefreshTokenCreator(TokenCreator):

    def create_token(self, payload: dict[str, Any]) -> str:
        expire_minutes = settings.jwt.refresh_expires_in_minutes
        exp = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=expire_minutes)

        return jwt.encode(
            payload={
                **payload,
                'type': TokenType.refresh.value,
                'exp': exp
            },
            key=settings.jwt.secret_key,
            algorithm=settings.jwt.algorithm
        )
