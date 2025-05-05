from fastapi.security import OAuth2PasswordRequestForm

from .utils import hash_password, verify_password
from .schemas import LoginUserOutput, VerifyEmailSchema
from .exceptions import PasswordIsIncorrect

from src.tokens import TokenService, TokenType

from src.users.schemas import UserCreate, UserRead
from src.users.user_services import UserService
from src.users.exceptions import UserNotVerifyEmail, UserAlreadyVerifiedEmail

from src.otp import OTPService


class AuthService:
    def __init__(
            self,
            user_service: UserService,
            token_service: TokenService,
            otp_service: OTPService,
    ):
        self._token_service = token_service
        self._user_service = user_service
        self._otp_service = otp_service

    async def _generate_and_save_tokens(self, user: UserRead) -> LoginUserOutput:
        """
        Helper function to generate access and refresh tokens, then save the refresh token.
        :param user: The user object for which to generate tokens.
        :return: LoginUserOutput containing the generated tokens.
        """
        access_token, refresh_token = self._token_service.get_access_and_refresh_tokens(user)
        await self._token_service.save_refresh_token(user.id, refresh_token)

        return LoginUserOutput(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='bearer'
        )

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

        await self._otp_service.send_and_save_otp(email=str(created.email))

        return created

    async def login_user(self, form_data: OAuth2PasswordRequestForm) -> LoginUserOutput:
        """        if not exists_user:
            raise UserWithUsernameNotFound(form_data.username)

        if not exists_user.is_verified:
            raise UserNotVerifyEmail

        Logs in the user and returns JWT tokens for authentication.

        :param form_data: OAuth2PasswordRequestForm instance with username and password.
        :return: LoginUserOutput containing access and refresh tokens.
        """
        exists_user = await self._user_service.get_by_username(form_data.username)

        if not exists_user.is_verified:
            raise UserNotVerifyEmail

        if not verify_password(
                plain_pass=form_data.password.encode(),
                hashed_password=exists_user.password.encode()
        ):
            raise PasswordIsIncorrect

        return await self._generate_and_save_tokens(exists_user)


    async def verify_user_by_otp_code(self, verify_data: VerifyEmailSchema) -> bool:
        user = await self._user_service.get_by_email(str(verify_data.email_user))

        if user.is_verified:
            raise UserAlreadyVerifiedEmail(str(user.email))

        return await self._otp_service.verify_otp(
            email=str(user.email),
            code=verify_data.otp_code
        )

    async def refresh_token(self, refresh_token: str) -> LoginUserOutput:
        payload = self._token_service.decode_token_with_token_type_checking(refresh_token, TokenType.refresh)
        user_id = int(payload['sub'])

        await self._token_service.verify_refresh_token(user_id, refresh_token)
        await self._token_service.delete_refresh_token(user_id)

        user: UserRead = await self._user_service.get_user_by_id(int(payload['sub']))

        return await self._generate_and_save_tokens(user)