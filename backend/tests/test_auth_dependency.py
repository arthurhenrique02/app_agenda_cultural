"""Tests for the get_current_user auth dependency (US-011)."""

import pytest
from httpx import AsyncClient

from app.security.jwt import create_access_token, create_refresh_token


@pytest.fixture
async def registered_user(async_client_with_tables: AsyncClient) -> dict:
    """Create a user and return their data plus a valid access token."""
    resp = await async_client_with_tables.post(
        "/api/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "secret123"},
    )
    assert resp.status_code == 201
    user = resp.json()
    token = create_access_token(str(user["id"]))
    return {"user": user, "token": token}


async def test_protected_route_without_token(
    async_client_with_tables: AsyncClient,
) -> None:
    """Protected route returns 401 when no Authorization header is provided."""
    resp = await async_client_with_tables.get("/api/users/me")
    assert resp.status_code == 401


async def test_protected_route_with_invalid_token(
    async_client_with_tables: AsyncClient,
) -> None:
    """Protected route returns 401 when an invalid/garbage token is sent."""
    resp = await async_client_with_tables.get(
        "/api/users/me",
        headers={"Authorization": "Bearer not_a_real_token"},
    )
    assert resp.status_code == 401


async def test_protected_route_with_refresh_token_returns_401(
    async_client_with_tables: AsyncClient,
) -> None:
    """Returns 401 when a refresh token is used instead of an access token."""
    # Register a user first
    await async_client_with_tables.post(
        "/api/auth/register",
        json={"name": "Bob", "email": "bob@example.com", "password": "secret123"},
    )
    refresh_token = create_refresh_token("1")
    resp = await async_client_with_tables.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert resp.status_code == 401


async def test_protected_route_with_valid_token(
    async_client_with_tables: AsyncClient,
    registered_user: dict,
) -> None:
    """Protected route returns 200 when a valid access token is provided."""
    token = registered_user["token"]
    resp = await async_client_with_tables.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "alice@example.com"


async def test_protected_route_returns_no_password_hash(
    async_client_with_tables: AsyncClient,
    registered_user: dict,
) -> None:
    """Protected route response does not expose the hashed_password field."""
    token = registered_user["token"]
    resp = await async_client_with_tables.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "hashed_password" not in resp.json()


async def test_token_for_nonexistent_user_returns_401(
    async_client_with_tables: AsyncClient,
) -> None:
    """Token referencing a user that does not exist returns 401."""
    token = create_access_token("99999")
    resp = await async_client_with_tables.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 401
