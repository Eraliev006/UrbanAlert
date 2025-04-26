from typing import Annotated

from fastapi.params import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.utils import decode_token
from src.core import database_helper
from src.users import UserRead, get_user_by_id

security = HTTPBearer()

async def get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        db_session: AsyncSession = Depends(database_helper.session_getter),
) -> UserRead:
    decoded_token = decode_token(credentials.credentials)
    user: UserRead = await get_user_by_id(db_session, decoded_token['user_id'])
    return user