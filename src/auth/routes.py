from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from src.auth import AuthService, LoginUserOutput, VerifyEmailSchema
from src.common import ErrorResponse
from src.core import get_auth_service
from src.tokens.schemas import RefreshTokenRequest
from src.users import UserRead, UserCreate

router = APIRouter(
    tags=['JWT Auth'],
    prefix='/auth',
)

AUTH_SERVICE_DEP = Annotated[AuthService, Depends(get_auth_service)]

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
async def register_user_route(user_data: UserCreate, auth_service: AUTH_SERVICE_DEP):
    return await auth_service.register_user(user_data)

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
async def login_user_router(auth_service: AUTH_SERVICE_DEP, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return await auth_service.login_user(form_data)

@router.post(
    '/verify-code',
    status_code=status.HTTP_200_OK,
    response_model=UserRead
)
async def verify_code_route(
        verify_data: VerifyEmailSchema,
        auth_service: AUTH_SERVICE_DEP
):
    return await auth_service.verify_user_by_otp_code(verify_data)

@router.post('/refresh')
async def refresh_token_route(
        refresh_token_request: RefreshTokenRequest,
        auth_service: AUTH_SERVICE_DEP
):
    return await auth_service.refresh_token(refresh_token_request.refresh_token)
