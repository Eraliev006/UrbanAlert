import logging
import os
import shutil
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel

from src.core import redis_client, database_helper
from src.main import app

# Register my fixtures
from .unit.user.fixtures import user_repository, user, fake_user, user_service, mock_user_repository, mock_user,mock_user_service, mock_user_create, mock_user_update, mock_users_list
from .unit.complaint.complaint_fixtures import  complaint_repository, fake_complaint, mock_complaint_repository, mock_complaint, mock_complaint_create, complaint_service, mock_complaint_update
from .unit.auth.auth_fixtures import mock_otp_service, mock_token_service, auth_service, mock_login_form_data, mock_verify_email_schema

@pytest_asyncio.fixture(scope='function')
async def test_engine():
    DATABASE_URL = "sqlite+aiosqlite:///./test.db"
    test_engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    return test_engine


@pytest_asyncio.fixture(scope='function')
async def tmp_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest_asyncio.fixture(scope='function')
async def session(test_engine, tmp_database):
    TestingSessionLocal = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
        expire_on_commit=False
    )
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="session", autouse=True)
def cleanup_test_artifacts():
    yield

    paths_to_remove = [
        "test.db",
        "fixkg_log.log",
        "static"
    ]

    for path in paths_to_remove:
        try:
            if os.path.isfile(path):
                os.remove(path)
                logging.info(f"Removed file: {path}")
            elif os.path.isdir(path):
                shutil.rmtree(path)
                logging.info(f"Removed directory: {path}")
        except Exception as e:
            logging.warning(f"Could not remove {path}: {e}")



@pytest_asyncio.fixture(scope='function')
async def async_client(session) -> AsyncGenerator[AsyncClient]:

    async def override_get_session():
        yield session

    app.dependency_overrides[database_helper.session_getter] = override_get_session

    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

@pytest_asyncio.fixture(scope='function')
def mock_image_service():
    mock_image_service = AsyncMock()
    return mock_image_service

@pytest_asyncio.fixture(scope="function")
async def redis_connection():
    await redis_client.connect()
    yield
    await redis_client.close()