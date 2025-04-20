from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from src.auth import register_user, LoginUserRead, login_user, LoginUserOutput
from src.common import ErrorResponse
from src.core import database_helper
from src.users import UserCreate, UserRead

router = APIRouter(
    tags=['JWT Auth'],
    prefix='/auth',
)

SESSION_DEP = Annotated[AsyncSession, Depends(database_helper.session_getter)]

@router.get('/me')
async def get_current_user():
    pass

@router.post('/register-user',
             response_model=UserRead,
             status_code=status.HTTP_201_CREATED,
             responses={
                status.HTTP_500_INTERNAL_SERVER_ERROR: {
                    'model': ErrorResponse,
                    'details': 'Error with database on server'
                },
                 status.HTTP_409_CONFLICT: {
                     'model': ErrorResponse,
                     'details': 'Email already registered'
                 }
             }
)
async def register_user_route(db_session: SESSION_DEP, user_data: UserCreate):
    return await register_user(db_session, user_data)

@router.post(
    '/login-user',
    response_model=LoginUserOutput,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': ErrorResponse,
            'details': 'Error with database on server'
        },
        status.HTTP_404_NOT_FOUND: {
            'model': ErrorResponse,
            'details': 'Email not found'
        },
        status.HTTP_403_FORBIDDEN: {
            'model': ErrorResponse,
            'details': 'User not verify email'
        },
    }
)
async def login_user_router(db_session: SESSION_DEP, login_data: LoginUserRead):
    return await login_user(db_session, login_data)

@router.post('/verify-code')
async def verify_code_route():
    pass

@router.post('/refresh')
async def refresh_token():
    pass
