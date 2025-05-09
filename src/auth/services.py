import logging
from fastapi.security import OAuth2PasswordRequestForm

from .utils import hash_password, verify_password
from .schemas import LoginUserOutput, VerifyEmailSchema
from .exceptions import PasswordIsIncorrect

from src.tokens import TokenService, TokenType
from src.users.schemas import UserCreate, UserRead
from src.users.user_services import UserService
from src.users.exceptions import UserNotVerifyEmail, UserAlreadyVerifiedEmail

from src.otp import OTPService
from src.users.models import User
from src.users import UserRepositories, UserWithUsernameNotFound, UserWithEmailNotFound

logger = logging.getLogger('fixkg.auth_service')

class AuthService:
    def __init__(
            self,
            user_service: UserService,
            token_service: TokenService,
            otp_service: OTPService,
            user_repo: UserRepositories
    ):
        self._token_service = token_service
        self._user_service = user_service
        self._otp_service = otp_service
        self._user_repo = user_repo

    async def _generate_and_save_tokens(self, user: User | UserRead) -> LoginUserOutput:
        logger.debug('Generating and saving tokens for user_id=%d', user.id)
        access_token, refresh_token = self._token_service.get_access_and_refresh_tokens(user)
        await self._token_service.save_refresh_token(user.id, refresh_token)

        logger.info('Tokens generated and saved for user_id=%d', user.id)
        return LoginUserOutput(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='bearer'
        )

    async def register_user(self, user: UserCreate) -> UserRead:
        logger.debug('Registering user with email=%s', user.email)

        user = UserCreate(
            **user.model_dump(exclude={'password'}),
            password=hash_password(user.password.encode())
        )

        created = await self._user_service.create_user(user)

        logger.info('User registered successfully with email=%s', created.email)

        await self._otp_service.send_and_save_otp(email=str(created.email))
        logger.debug('OTP sent and saved for email=%s', created.email)

        return created

    async def login_user(self, form_data: OAuth2PasswordRequestForm) -> LoginUserOutput:
        logger.debug('Login attempt for username=%s', form_data.username)
        exists_user = await self._user_repo.get_by_username(form_data.username)

        if not exists_user:
            logger.error('User with username=%s not found', form_data.username)
            raise UserWithUsernameNotFound(username=form_data.username)

        if not exists_user.is_verified:
            logger.warning('User with username=%s is not verified', form_data.username)
            raise UserNotVerifyEmail

        if not verify_password(
                plain_pass=form_data.password.encode(),
                hashed_password=exists_user.password.encode()
        ):
            logger.error('Incorrect password for username=%s', form_data.username)
            raise PasswordIsIncorrect

        logger.info('User with username=%s logged in successfully', form_data.username)
        return await self._generate_and_save_tokens(exists_user)

    async def verify_user_by_otp_code(self, verify_data: VerifyEmailSchema) -> UserRead:
        logger.debug('Verifying user with email=%s by OTP', verify_data.email_user)

        user = await self._user_repo.get_by_email(str(verify_data.email_user))

        if not user:
            logger.error('User with email=%s not found', verify_data.email_user)
            raise UserWithEmailNotFound(str(verify_data.email_user))

        if user.is_verified:
            logger.warning('User with email=%s is already verified', user.email)
            raise UserAlreadyVerifiedEmail(str(user.email))

        await self._otp_service.verify_otp(
            email=str(user.email),
            code=verify_data.otp_code
        )
        logger.info('OTP verified successfully for email=%s', user.email)

        verified_user = await self._user_repo.set_verified(user, verified=True)
        logger.info('User with email=%s verified successfully', user.email)
        return UserRead(**verified_user.model_dump())

    async def refresh_token(self, refresh_token: str) -> LoginUserOutput:
        logger.debug('Refreshing token with refresh_token=%s', refresh_token)
        payload = self._token_service.decode_token_with_token_type_checking(refresh_token, TokenType.refresh)
        user_id = int(payload['sub'])

        await self._token_service.verify_refresh_token(user_id, refresh_token)
        await self._token_service.delete_refresh_token(user_id)

        user: UserRead = await self._user_service.get_user_by_id(user_id)

        logger.info('Tokens refreshed for user_id=%d', user_id)
        return await self._generate_and_save_tokens(user)
