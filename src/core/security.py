from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.auth.utils import decode_token
from .dependencies import get_user_service
from src.users import UserRead, UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login-user')

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        user_service: Annotated[UserService, Depends(get_user_service)]

) -> UserRead:
    decoded_token = decode_token(token)
    user: UserRead = await user_service.get_user_by_id(decoded_token['user_id'])
    return user