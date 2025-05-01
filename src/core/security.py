from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from .dependencies import get_user_service, get_token_service
from src.users import UserRead, UserService
from ..tokens import TokenService, TokenType

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login-user')

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        token_service: Annotated[TokenService, Depends(get_token_service)]
) -> UserRead:
    decoded_token = token_service.decode_token_with_token_type_checking(token, TokenType.access)
    user: UserRead = await user_service.get_user_by_id(int(decoded_token['sub']))
    return user