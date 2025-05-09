from logging import getLogger
from fastapi import UploadFile

from src.users.models import User
from .schemas import UserRead, UserCreate, UserUpdate
from .exceptions import (
    UserWithIdNotFound,
    EmailOrUsernameAlreadyExists,
    UserWithUsernameNotFound,
    UserWithEmailNotFound
)
from .repositories import UserRepositories
from src.images import ImageService


logger = getLogger('fixkg.user_service')


class UserService:
    def __init__(self, user_repo: UserRepositories, image_service: ImageService):
        logger.debug('UserService initialized with user_repo=%s, image_service=%s', user_repo, image_service)
        self._user_repo = user_repo
        self._image_service = image_service

    async def _check_if_user_exists(
            self,
            email: str,
            username: str
    ) -> bool:
        logger.debug('Checking if user exists with email=%s and username=%s', email, username)
        return await self._user_repo.get_by_email_or_username(email, username) is not None

    async def get_all_users(self) -> list[UserRead]:
        logger.info('Getting all users')
        users = await self._user_repo.get_all()
        logger.debug('Found %d users', len(users))
        logger.info('Return list of users')
        return [UserRead(**user.model_dump()) for user in users]

    async def create_user(self, user: UserCreate) -> UserRead:
        logger.info('Creating user: email=%s, username=%s', user.email, user.username)
        if await self._check_if_user_exists(str(user.email), user.username):
            logger.warning('Email or username already exists: email=%s, username=%s', user.email, user.username)
            logger.error('Call EmailOrUsernameAlreadyExists exceptions')
            raise EmailOrUsernameAlreadyExists(str(user.email), user.username)

        user_in_db = User(**user.model_dump())
        created = await self._user_repo.create(user_in_db)

        logger.info('User created with id=%s', created.id)
        logger.debug('Created user data: %s', created.model_dump())
        logger.info('Return created user')
        return UserRead(**created.model_dump())

    async def get_user_by_id(self, user_id: int) -> UserRead:
        logger.info('Getting user by id=%d', user_id)
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            logger.warning('User not found with id=%d', user_id)
            logger.info('Calling UserWithIdNotFound exceptions')
            raise UserWithIdNotFound(user_id)

        logger.info('Returned user by id=%d', user.id)
        return UserRead(**user.model_dump())

    async def update_user_by_id(self, user_id: int, new_user_data: UserUpdate) -> UserRead:
        logger.info('Updating user by id=%d', user_id)
        user = await self._user_repo.get_by_id(user_id)

        if not user:
            logger.warning('User not found with id=%d', user_id)
            logger.info('Calling UserWithIdNotFound exceptions')
            raise UserWithIdNotFound(user_id)

        if await self._check_if_user_exists(str(new_user_data.email), new_user_data.username):
            logger.warning('Email or username already exists: email=%s, username=%s',
                           new_user_data.email, new_user_data.username)
            raise EmailOrUsernameAlreadyExists(
                str(new_user_data.email),
                new_user_data.username
            )

        updated = await self._user_repo.update(
            user=user,
            new_data=new_user_data
        )
        logger.info('User updated: id=%s', updated.id)
        return UserRead(**updated.model_dump())

    async def delete_user_by_id(self, user_id: int) -> None:
        logger.info('Deleting user by id=%d', user_id)
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            logger.warning('User not found with id=%d', user_id)
            raise UserWithIdNotFound(user_id)

        await self._user_repo.delete(user)
        logger.info('User deleted: id=%d', user_id)
        return None

    async def get_by_username(self, username: str) -> UserRead:
        logger.info('Getting user by username=%s', username)
        user = await self._user_repo.get_by_username(username)

        if not user:
            logger.warning('User not found with username=%s', username)
            raise UserWithUsernameNotFound(username)

        logger.info('Returned user by username=%s', username)
        return UserRead(**user.model_dump())

    async def get_by_email(self, email: str) -> UserRead:
        logger.info('Getting user by email=%s', email)
        user = await self._user_repo.get_by_email(email)

        if not user:
            logger.warning('User not found with email=%s', email)
            raise UserWithEmailNotFound(email)

        logger.info('Returned user by email=%s', email)
        return UserRead(**user.model_dump())

    async def save_user_avatar_image(self, file: UploadFile, user_id: int) -> UserRead:
        logger.info('Saving avatar image for user_id=%d, filename=%s', user_id, file.filename)
        await self.get_user_by_id(user_id)

        avatar_url = await self._image_service.save_user_avatar_image(file, user_id)
        logger.info('Avatar saved at: %s', avatar_url)

        updated_user = await self._user_repo.save_user_avatar(
            avatar_url=avatar_url,
            user_id=user_id
        )

        logger.info('User avatar updated for user_id=%d', user_id)
        return UserRead(**updated_user.model_dump())
