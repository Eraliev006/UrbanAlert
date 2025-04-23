from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import EmailAlreadyExists, hash_password, LoginUserRead, LoginUserOutput, UserWithEmailNotFound, \
    verify_password, PasswordIsIncorrect, TokenPairs, UserNotVerifyEmail
from src.auth.utils import get_pairs_token, generate_otp_code
from src.notification import NotifierType
from src.notification.notifier_factory import NotifierFactory
from src.users import UserCreate, User, UserRead
from src.users import get_user_by_email, create_user


async def register_user(db_session: AsyncSession, user:UserCreate) -> UserRead:
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

    return UserRead(**created_user.model_dump())


async def login_user(db_session: AsyncSession,login_data: LoginUserRead) -> LoginUserOutput:
    exists_user: Optional[User] = await get_user_by_email(db_session, str(login_data.email))

    if not exists_user:
        raise UserWithEmailNotFound(str(login_data.email))

    if not exists_user.is_verified:
        raise UserNotVerifyEmail

    if not verify_password(
        plain_pass=login_data.password.encode(),
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



