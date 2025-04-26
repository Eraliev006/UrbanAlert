from datetime import timedelta
from typing import Optional

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import EmailAlreadyExists, hash_password, LoginUserOutput, \
    verify_password, PasswordIsIncorrect, TokenPairs, UserNotVerifyEmail, VerifyEmailSchema, OTPCodeNotFoundOrExpired, \
    OTPCodeIsWrong, UserAlreadyVerifiedEmail, UserWithUsernameNotFound, UserWithEmailNotFound, InvalidTokenType
from src.auth.utils import get_pairs_token, generate_otp_code, decode_token
from src.core import redis_client
from src.notification import NotifierType
from src.notification.notifier_factory import NotifierFactory
from src.users import UserCreate, User, UserRead, change_user_is_verify_status, get_user_by_email
from src.users import get_user_by_username, create_user


async def register_user(db_session: AsyncSession, user:UserCreate) -> UserRead:
    """
    Function is register user in app.
    Return EmailAlreadyExists exception if email already exists. Also return UserRead
    :param user: getting the UserCreate instance to insert to db
    :param db_session: takes session to make transaction with database
    """
    exists_user: Optional[User] = await get_user_by_email(db_session,str(user.email))

    if exists_user:
        raise EmailAlreadyExists(str(user.email))

    hashed_password: str = hash_password(user.password.encode())
    user = UserCreate(
        **user.model_dump(exclude={'password'}),
        password = hashed_password
    )

    created_user: Optional[User] = await create_user(
        db_session,
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
        key = f'otp:{created_user.email}',
        value = otp_code,
        ex = timedelta(minutes=5)
    )

    return UserRead(**created_user.model_dump())


async def login_user(db_session: AsyncSession,form_data: OAuth2PasswordRequestForm) -> LoginUserOutput:
    """
    Function is login user in app.
    Return UserWithUsernameNotFound exception if email not exists.
    Return UserNotVerifyEmail if current user is not verify email
    Return PasswordIsIncorrect if password is incorrect
    Return LoginUserOutput if password and username is correct
    :param form_data: getting the OAuth2PasswordRequestForm instance to check is user registered and check password and email
    :param db_session: takes session to make transaction with database
    """
    exists_user: Optional[User] = await get_user_by_username(db_session, form_data.username)

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
    tokens: TokenPairs = get_pairs_token(payload)

    return LoginUserOutput(
        access_token = tokens.access_token,
        refresh_token = tokens.refresh_token,
        token_type = 'bearer'
    )

async def verify_user_by_otp_code(db_session: AsyncSession, verify_data: VerifyEmailSchema) -> dict[str, str]:
    user = await get_user_by_email(db_session, str(verify_data.email_user))

    if not user:
        raise UserWithEmailNotFound(str(verify_data.email_user))

    if user.is_verified:
        raise UserAlreadyVerifiedEmail(str(user.email))

    saved_otp_code = await redis_client.get(f'otp:{verify_data.email_user}')
    if saved_otp_code is None:
        raise OTPCodeNotFoundOrExpired(str(user.email))

    if saved_otp_code != verify_data.otp_code:
        raise OTPCodeIsWrong

    await change_user_is_verify_status(db_session, user)
    return {"message": "User verification successful"}

async def refresh_token(refresh_token: str) -> LoginUserOutput:
    payload = decode_token(refresh_token)

    if payload['type'] != 'refresh':
        raise InvalidTokenType
    tokens: TokenPairs = get_pairs_token(payload)

    return LoginUserOutput(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type='bearer'
    )

