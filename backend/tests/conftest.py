"""Shared pytest fixtures for the Agenda Cultural backend test suite."""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import database as db_module
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an isolated in-memory AsyncSession for each test.

    Creates a fresh SQLite engine and session per test to ensure
    full isolation without needing a running PostgreSQL instance.
    """
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an httpx AsyncClient wired to the FastAPI app.

    Overrides the app's get_db dependency to use the test db_session
    so all requests are served from the isolated in-memory DB.
    """
    # Override AsyncSessionLocal so get_db yields the test session
    original_factory = db_module.AsyncSessionLocal

    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    test_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    db_module.AsyncSessionLocal = test_factory

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            yield client
    finally:
        db_module.AsyncSessionLocal = original_factory
        await test_engine.dispose()
