import logging
import os
import shutil
from typing import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel

from src.main import app

# Register my fixtures
from .unit.user.fixtures import user_repository, user, fake_user
from .unit.complaint.complaint_fixtures import  complaint_repository, fake_complaint


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


@pytest_asyncio.fixture(scope='session')
async def async_client(tmp_database) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url=""
    ) as ac:
        yield ac
