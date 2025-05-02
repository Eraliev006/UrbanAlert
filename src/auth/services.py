from datetime import timedelta
from typing import Optional

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src import User
from src.auth import hash_password, LoginUserOutput, \
    verify_password, PasswordIsIncorrect,VerifyEmailSchema, OTPCodeNotFoundOrExpired, \
    OTPCodeIsWrong, generate_otp_code
from src.notification import EmailNotificationService
from src.tokens import TokenService, TokenType, RefreshTokenNotFound, InvalidSignatureException
from src.core import redis_client
from src.users import UserCreate, UserRead, UserService, UserWithUsernameNotFound, UserNotVerifyEmail, \
    UserWithEmailNotFound, UserAlreadyVerifiedEmail
from src.users import EmailOrUsernameAlreadyExists


class AuthService:
    def __init__(self,db: AsyncSession, user_service: UserService, token_service: TokenService, email_service: EmailNotificationService):
        self.token_service = token_service
        self.user_service = user_service
        self.email_service = email_service
        self.db = db

    async def register_user(self, user: UserCreate) -> UserRead:
        """
        Function is register user in app.
        Return EmailAlreadyExists exception if email already exists. Also return UserRead
        :param user: getting the UserCreate instance to insert to db
        """
        exists_user: Optional[User] = await self.user_service.get_user_by_email_or_username(str(user.email), user.username)

        if exists_user:
            raise EmailOrUsernameAlreadyExists(str(user.email), user.username)

        hashed_password: str = hash_password(user.password.encode())
        user = UserCreate(
            **user.model_dump(exclude={'password'}),
            password=hashed_password
        )

        created_user: Optional[User] = await self.user_service.create_user(
            user
        )

        otp_code = generate_otp_code()

        await self.email_service.send_otp(
            to_email=str(created_user.email),
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

        access_token, refresh_token = self.token_service.get_access_and_refresh_tokens(exists_user)

        await self.token_service.save_refresh_token(exists_user.id, refresh_token)

        return LoginUserOutput(
            access_token=access_token,
            refresh_token=refresh_token,
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

    async def refresh_token(self, refresh_token: str) -> LoginUserOutput:
        payload = self.token_service.decode_token_with_token_type_checking(refresh_token, TokenType.refresh)
        user_id = int(payload['sub'])

        exists_refresh_token = await self.token_service.get_refresh_token(user_id)

        if not exists_refresh_token:
            raise RefreshTokenNotFound

        if exists_refresh_token != refresh_token:
            raise InvalidSignatureException

        await self.token_service.delete_refresh_token(user_id)
        user: UserRead = await self.user_service.get_user_by_id(int(payload['sub']))

        new_access_token, new_refresh_token = self.token_service.get_access_and_refresh_tokens(user)

        await self.token_service.save_refresh_token(user_id, new_refresh_token)
        return LoginUserOutput(
            access_token = new_access_token,
            refresh_token = new_refresh_token,
            token_type = 'bearer'
        )