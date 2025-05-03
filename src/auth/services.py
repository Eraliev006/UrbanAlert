from datetime import timedelta
from typing import Optional

from fastapi.security import OAuth2PasswordRequestForm

from src import User

from .utils import hash_password, verify_password, generate_otp_code
from .schemas import LoginUserOutput, VerifyEmailSchema
from .exceptions import PasswordIsIncorrect, OTPCodeNotFoundOrExpired, OTPCodeIsWrong

from src.notification import EmailNotificationService
from src.tokens import TokenService, TokenType, RefreshTokenNotFound, InvalidSignatureException
from src.core import redis_client

from src.users.schemas import UserCreate, UserRead
from src.users.user_services import UserService
from src.users.repositories import UserRepositories
from src.users.exceptions import UserWithUsernameNotFound, UserNotVerifyEmail, UserWithEmailNotFound, \
    UserAlreadyVerifiedEmail


class AuthService:
    def __init__(

            self,
            user_service: UserService,
            token_service: TokenService,
            email_service: EmailNotificationService,
            user_repo: UserRepositories,
    ):
        self._token_service = token_service
        self._user_service = user_service
        self._email_service = email_service
        self._user_repo = user_repo

    async def register_user(self, user: UserCreate) -> UserRead:
        """
        Function is register user in app.
        Return EmailAlreadyExists exception if email already exists. Also return UserRead
        :param user: getting the UserCreate instance to insert to db
        """

        user = UserCreate(
            **user.model_dump(exclude={'password'}),
            password=hash_password(user.password.encode())
        )

        created = await self._user_service.create_user(user)

        otp_code = generate_otp_code()

        await self._email_service.send_otp(
            to_email=str(created.email),
            otp_code=otp_code
        )

        await redis_client.set(
            key=f'otp:{created.email}',
            value=otp_code,
            ex=timedelta(minutes=5)
        )

        return created

    async def login_user(self, form_data: OAuth2PasswordRequestForm) -> LoginUserOutput:
        """
        Logs in the user and returns JWT tokens for authentication.

        :param form_data: OAuth2PasswordRequestForm instance with username and password.
        :return: LoginUserOutput containing access and refresh tokens.
        """
        exists_user: Optional[User] = await self._user_repo.get_by_username(form_data.username)

        if not exists_user:
            raise UserWithUsernameNotFound(form_data.username)

        if not exists_user.is_verified:
            raise UserNotVerifyEmail

        if not verify_password(
                plain_pass=form_data.password.encode(),
                hashed_password=exists_user.password.encode()
        ):
            raise PasswordIsIncorrect

        access_token, refresh_token = self._token_service.get_access_and_refresh_tokens(exists_user)

        await self._token_service.save_refresh_token(exists_user.id, refresh_token)

        return LoginUserOutput(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='bearer'
        )


    async def verify_user_by_otp_code(self, verify_data: VerifyEmailSchema) -> dict[str, str]:
        user = await self._user_repo.get_by_email(str(verify_data.email_user))

        if not user:
            raise UserWithEmailNotFound(str(verify_data.email_user))

        if user.is_verified:
            raise UserAlreadyVerifiedEmail(str(user.email))

        saved_otp_code = await redis_client.get(f'otp:{verify_data.email_user}')
        if saved_otp_code is None:
            raise OTPCodeNotFoundOrExpired(str(user.email))

        if saved_otp_code != verify_data.otp_code:
            raise OTPCodeIsWrong

        await self._user_repo.set_verified(user, verified=True)
        return {"message": "User verification successful"}

    async def refresh_token(self, refresh_token: str) -> LoginUserOutput:
        payload = self._token_service.decode_token_with_token_type_checking(refresh_token, TokenType.refresh)
        user_id = int(payload['sub'])

        exists_refresh_token = await self._token_service.get_refresh_token(user_id)

        if not exists_refresh_token:
            raise RefreshTokenNotFound

        if exists_refresh_token != refresh_token:
            raise InvalidSignatureException

        await self._token_service.delete_refresh_token(user_id)
        user: UserRead = await self._user_service.get_user_by_id(int(payload['sub']))

        new_access_token, new_refresh_token = self._token_service.get_access_and_refresh_tokens(user)

        await self._token_service.save_refresh_token(user_id, new_refresh_token)
        return LoginUserOutput(
            access_token = new_access_token,
            refresh_token = new_refresh_token,
            token_type = 'bearer'
        )