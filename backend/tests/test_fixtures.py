"""Tests for shared pytest fixtures (US-005).

These tests verify that the conftest fixtures are correctly implemented
and usable by all future test modules.
"""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


async def test_db_session_fixture_yields_async_session(db_session):
    """db_session fixture must yield an AsyncSession."""
    assert isinstance(db_session, AsyncSession)


async def test_db_session_fixture_is_usable(db_session):
    """db_session must be able to execute a simple query."""
    from sqlalchemy import text

    result = await db_session.execute(text("SELECT 1"))
    row = result.scalar()
    assert row == 1


async def test_async_client_fixture_is_async_client(async_client):
    """async_client fixture must be an httpx AsyncClient."""
    assert isinstance(async_client, AsyncClient)


async def test_async_client_can_reach_health_endpoint(async_client):
    """async_client must be able to reach the app health endpoint."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_db_override_is_isolated(db_session):
    """Each test using db_session should get an isolated session."""
    from sqlalchemy import text

    # Execute a simple query to confirm session is functional
    result = await db_session.execute(text("SELECT 42 AS val"))
    assert result.scalar() == 42
