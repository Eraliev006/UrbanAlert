from src import User
from .schemas import UserRead, UserCreate, UserUpdate
from .exceptions import UserWithIdNotFound, EmailOrUsernameAlreadyExists
from .repositories import UserRepositories


class UserService:
    def __init__(self, user_repo: UserRepositories):
        self._user_repo = user_repo

    async def _check_if_user_exists(
            self,
            email: str,
            username: str
    ) -> bool:
        return await self._user_repo.get_by_email_or_username(email, username) is not None

    async def get_all_users(self) -> list[UserRead]:
        users = await self._user_repo.get_all()

        return [UserRead(**user.model_dump()) for user in users]

    async def create_user(self, user: UserCreate) -> UserRead:
        if await self._check_if_user_exists(str(user.email), user.username):
            raise EmailOrUsernameAlreadyExists(str(user.email), user.username)

        user_in_db = User(**user.model_dump())

        created = await self._user_repo.create(user_in_db)

        return UserRead(**created.model_dump())


    async def get_user_by_id(self, user_id: int) -> UserRead:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserWithIdNotFound(user_id)

        return UserRead(**user.model_dump())

    async def update_user_by_id(self, user_id: int, new_user_data: UserUpdate) -> UserRead:
        user = await self._user_repo.get_by_id(user_id)

        if not user:
            raise UserWithIdNotFound(user_id)

        if await self._check_if_user_exists(str(new_user_data.email), new_user_data.username):
            raise EmailOrUsernameAlreadyExists(
                str(new_user_data.email),
                new_user_data.username
            )

        updated = await self._user_repo.update(
            user = user,
            new_data = new_user_data
        )
        return UserRead(**updated.model_dump())

    async def delete_user_by_id(self, user_id: int) -> None:
        """
        Async method to delete user by ID.
        :param user_id: ID of the user to delete.
        """
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserWithIdNotFound(user_id)

        await self._user_repo.delete(user)
        return None
