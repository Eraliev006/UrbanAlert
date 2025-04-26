from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from src.common import ErrorResponse
from src.core import database_helper, get_current_user
from src.users import get_user_by_id, update_user_by_id, UserUpdate, delete_user_by_id, get_all_users, UserRead

router = APIRouter(
    tags=['Users'],
    prefix='/users',
)

common_responses = {
    status.HTTP_404_NOT_FOUND: {
        'model': ErrorResponse,
        'details': 'User with id not found',
    }
}

SESSION_DEP = Annotated[AsyncSession, Depends(database_helper.session_getter)]
CURRENT_USER_DEP = Annotated[UserRead, Depends(get_current_user)]

@router.get(
    '/',
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK,
    responses={},
)
async def get_all_users_route(session: SESSION_DEP):
    return await get_all_users(session)

@router.get('/me')
async def get_current_user_route(
        current_user: CURRENT_USER_DEP
):
    return current_user

@router.get(
    '/{user_id}',
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    responses={
        **common_responses,
    }
)
async def get_user_by_id_route(user_id: int, session: SESSION_DEP):
    return await get_user_by_id(session, user_id)

@router.patch(
    '/me',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=UserRead,
    responses={
        **common_responses,
    }
)
async def update_user_by_id_route(
        new_user_data: UserUpdate,
        session: SESSION_DEP,
        current_user: CURRENT_USER_DEP
):
    return await update_user_by_id(session, current_user.id, new_user_data)

@router.delete(
    '/me',
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    responses={
        **common_responses
    }
)
async def delete_user_by_id_route(
        session: SESSION_DEP,
        current_user: CURRENT_USER_DEP,
):
    return await delete_user_by_id(session, current_user.id)
