from typing import Annotated

from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.utils import decode_token
from src.core import database_helper
from src.users import UserRead, get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login-user')

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db_session: AsyncSession = Depends(database_helper.session_getter),
) -> UserRead:
    decoded_token = decode_token(token)
    user: UserRead = await get_user_by_id(db_session, decoded_token['user_id'])
    return user