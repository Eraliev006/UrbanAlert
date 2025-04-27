from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from src.common import ErrorResponse
from src.core import get_current_user, get_user_service
from src.users import UserRead, UserUpdate, UserService

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

CURRENT_USER_DEP = Annotated[UserRead, Depends(get_current_user)]
USER_SERVICE_DEP = Annotated[UserService, Depends(get_user_service)]


@router.get(
    '/',
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK,
)
async def get_all_users_route(service: USER_SERVICE_DEP) -> list[UserRead]:
    return await service.get_all_users()

@router.get('/me')
async def get_current_user_route(current_user: CURRENT_USER_DEP) -> UserRead:
    return current_user


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
    service: USER_SERVICE_DEP,
    current_user: CURRENT_USER_DEP,
) -> UserRead:
    return await service.update_user_by_id(current_user.id, new_user_data)


@router.delete(
    '/me',
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    responses={
        **common_responses,
    }
)
async def delete_user_by_id_route(
    service: USER_SERVICE_DEP,
    current_user: CURRENT_USER_DEP,
) -> None:
    await service.delete_user_by_id(current_user.id)


@router.get(
    '/{user_id}',
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    responses={
        **common_responses,
    }
)
async def get_user_by_id_route(
    user_id: int,
    service: USER_SERVICE_DEP,
) -> UserRead:
    return await service.get_user_by_id(user_id)
