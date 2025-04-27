from datetime import timedelta
from typing import Optional

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src import User
from src.auth import hash_password, LoginUserOutput, \
    verify_password, PasswordIsIncorrect, TokenPairs, UserNotVerifyEmail, VerifyEmailSchema, OTPCodeNotFoundOrExpired, \
    OTPCodeIsWrong, UserAlreadyVerifiedEmail, UserWithUsernameNotFound, UserWithEmailNotFound, InvalidTokenType, EmailOrUsernameAlreadyExists, \
    NewAccessToken, get_pairs_token, generate_otp_code, decode_token, RefreshTokenNotFound
from src.auth.tokens.access import AccessTokenCreator
from src.auth.tokens.token_repository import TokenRepository
from src.core import redis_client
from src.notification import NotifierType, NotifierFactory
from src.users import UserCreate, UserRead, UserService


class AuthService:
    def __init__(self,db: AsyncSession, user_service: UserService, token_repo: TokenRepository):
        self.token_repo = token_repo
        self.user_service = user_service
        self.db = db

    async def register_user(self, user: UserCreate) -> UserRead:
        """
        Function is register user in app.
        Return EmailAlreadyExists exception if email already exists. Also return UserRead
        :param user: getting the UserCreate instance to insert to db
        """
        exists_user: Optional[User] = await self.user_service.get_user_by_email_or_username(str(user.email), user.username)

        if exists_user:
            raise EmailOrUsernameAlreadyExists(str(user.email), exists_user.username)

        hashed_password: str = hash_password(user.password.encode())
        user = UserCreate(
            **user.model_dump(exclude={'password'}),
            password=hashed_password
        )

        created_user: Optional[User] = await self.user_service.create_user(
            user
        )

        # Add notify to celery tasks
        otp_code = generate_otp_code()
        notifier = NotifierFactory.get_notifier(NotifierType.EMAIL)

        await notifier.notify(
            to_user=str(created_user.email),
            otp_code=otp_code
        )

        await redis_client.set(
            key=f'otp:{created_user.email}',
            value=otp_code,
            ex=timedelta(minutes=5)
        )

        return UserRead(**created_user.model_dump())


    async def login_user(self, form_data: OAuth2PasswordRequestForm) -> LoginUserOutput:
        """
        Logs in the user and returns JWT tokens for authentication.

        :param form_data: OAuth2PasswordRequestForm instance with username and password.
        :return: LoginUserOutput containing access and refresh tokens.
        """
        exists_user: Optional[User] = await self.user_service.get_user_by_username(form_data.username)

        if not exists_user:
            raise UserWithUsernameNotFound(form_data.username)

        if not exists_user.is_verified:
            raise UserNotVerifyEmail

        if not verify_password(
                plain_pass=form_data.password.encode(),
                hashed_password=exists_user.password.encode()
        ):
            raise PasswordIsIncorrect

        payload = {
            'sub': 'user',
            'user_id': exists_user.id,
            'is_verified': exists_user.is_verified
        }
        token_pairs: TokenPairs = get_pairs_token(payload)

        await self.token_repo.save_refresh_token(exists_user.id, token_pairs.refresh_token)

        return LoginUserOutput(
            access_token=token_pairs.access_token,
            refresh_token=token_pairs.refresh_token,
            token_type='bearer'
        )


    async def verify_user_by_otp_code(self, verify_data: VerifyEmailSchema) -> dict[str, str]:
        user = await self.user_service.get_user_by_email(str(verify_data.email_user))

        if not user:
            raise UserWithEmailNotFound(str(verify_data.email_user))

        if user.is_verified:
            raise UserAlreadyVerifiedEmail(str(user.email))

        saved_otp_code = await redis_client.get(f'otp:{verify_data.email_user}')
        if saved_otp_code is None:
            raise OTPCodeNotFoundOrExpired(str(user.email))

        if saved_otp_code != verify_data.otp_code:
            raise OTPCodeIsWrong

        await self.user_service.change_user_is_verify_status(user)
        return {"message": "User verification successful"}

    async def refresh_token(self, refresh_token: str) -> NewAccessToken:
        payload = decode_token(refresh_token)
        user_id = payload['user_id']

        if payload['type'] != 'refresh':
            raise InvalidTokenType

        exists_refresh_token = await self.token_repo.get_refresh_token(user_id)

        if not exists_refresh_token:
            raise RefreshTokenNotFound

        new_access_token: str = AccessTokenCreator().generate(payload)

        return NewAccessToken(new_access_token = new_access_token)

