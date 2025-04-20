import datetime
from unittest.mock import MagicMock

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth import UserWithEmailNotFound
from src.common import IntegrityErrorException, DatabaseError
from src.users import create_user, UserCreate, User, get_user_by_id, UserWithIdNotFound, UserRead, update_user_by_id, \
    UserUpdate, delete_user_by_id, get_user_by_email


@pytest.mark.asyncio
async def test_create_user_success(session, fake_user_create_data: UserCreate):

    created_user = await create_user(session, fake_user_create_data)

    assert isinstance(created_user, User)
    assert created_user.email == fake_user_create_data.email
    assert created_user.first_name == fake_user_create_data.first_name
    assert created_user.created_at == datetime.date.today()
    assert created_user.is_verified == False

@pytest.mark.asyncio
async def test_create_user_integrity_error(session, fake_user_create_data):
    await create_user(session, fake_user_create_data)
    with pytest.raises(IntegrityErrorException):
        await create_user(session, fake_user_create_data)

@pytest.mark.asyncio
async def test_create_user_sqlalchemy_error(session, fake_user_create_data):

    db_session = MagicMock()
    db_session.add = MagicMock()
    db_session.commit = MagicMock(side_effect=DatabaseError('Error with DB while creating user'))

    with pytest.raises(DatabaseError, match='Error with DB while creating user'):
        await create_user(db_session, fake_user_create_data)


@pytest.mark.asyncio
async def test_get_user_by_id(session: AsyncSession, fake_user_create_data: UserCreate):
    created_user: User = await create_user(session, fake_user_create_data)

    exists_user: UserRead = await get_user_by_id(session, created_user.id)

    assert isinstance(exists_user, UserRead)
    assert created_user.email == exists_user.email

@pytest.mark.asyncio
async def test_get_user_by_id_not_found(session):
    invalid_id = 131231230

    db_session = MagicMock()
    db_session._get_user_by_id = MagicMock(return_value = None)

    with pytest.raises(UserWithIdNotFound):
        await get_user_by_id(session,invalid_id)

@pytest.mark.asyncio
async def test_user_update_success(session, fake_user_create_data, fake_user_update_data):
    created_user = await create_user(session, fake_user_create_data)

    updated = await update_user_by_id(session, created_user.id, fake_user_update_data)

    assert isinstance(updated, UserRead)
    assert updated.email != fake_user_create_data.email
    assert updated.email == fake_user_update_data.email
    assert updated.id == created_user.id

@pytest.mark.asyncio
async def test_user_update_not_found(session, fake_user_create_data, fake_user_update_data):
    await create_user(session, fake_user_create_data)
    incorrect_ids = 87677912

    with pytest.raises(UserWithIdNotFound):
        await get_user_by_id(session, incorrect_ids)

@pytest.mark.asyncio
async def test_user_delete_success(session, fake_user_create_data, fake_user_update_data):
    created = await create_user(session, fake_user_create_data)

    await delete_user_by_id(session, created.id)

    with pytest.raises(UserWithIdNotFound):
        await get_user_by_id(session, created.id)


@pytest.mark.asyncio
async def test_user_delete_not_found(session, fake_user_create_data):
    await create_user(session, fake_user_create_data)
    incorrect_ids = 87677912

    with pytest.raises(UserWithIdNotFound):
        await delete_user_by_id(session, incorrect_ids)

@pytest.mark.asyncio
async def test_get_user_by_email_success(session, fake_user_create_data):
    created = await create_user(session, fake_user_create_data)

    user = await get_user_by_email(session, str(created.email))

    assert user
    assert fake_user_create_data.email == user.email
    assert isinstance(user, User)

