"""Tests for async SQLAlchemy session configuration (US-003)."""

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker


def test_database_module_exports_engine():
    """database module must export an AsyncEngine instance."""
    from app.database import engine

    assert isinstance(engine, AsyncEngine)


def test_database_module_exports_async_session_factory():
    """database module must export an async_sessionmaker."""
    from app.database import AsyncSessionLocal

    assert isinstance(AsyncSessionLocal, async_sessionmaker)


def test_database_url_matches_settings():
    """Engine URL should match settings.database_url."""
    from app.config import settings
    from app.database import engine

    # render_as_string(hide_password=False) returns the full URL without masking
    engine_url = engine.url.render_as_string(hide_password=False)
    assert engine_url == settings.database_url


async def test_get_db_yields_async_session(tmp_path):
    """get_db dependency must yield an AsyncSession."""
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )

    from app import database as db_module
    from app.dependencies.database import get_db

    # Create a lightweight in-memory SQLite engine for test isolation
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    test_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)

    original_factory = db_module.AsyncSessionLocal
    db_module.AsyncSessionLocal = test_session_factory
    try:
        gen = get_db()
        session = await gen.__anext__()
        assert isinstance(session, AsyncSession)
        await gen.aclose()
    finally:
        db_module.AsyncSessionLocal = original_factory
        await test_engine.dispose()


async def test_get_db_as_fastapi_dependency():
    """FastAPI app using get_db dependency should handle requests without errors."""
    from fastapi import Depends
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )

    from app import database as db_module
    from app.dependencies.database import get_db

    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    test_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)

    original_factory = db_module.AsyncSessionLocal
    db_module.AsyncSessionLocal = test_session_factory

    test_app = FastAPI()

    @test_app.get("/test-db")
    async def test_route(db: AsyncSession = Depends(get_db)):
        return {"session_type": type(db).__name__}

    try:
        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.get("/test-db")
            assert response.status_code == 200
            assert response.json()["session_type"] == "AsyncSession"
    finally:
        db_module.AsyncSessionLocal = original_factory
        await test_engine.dispose()
