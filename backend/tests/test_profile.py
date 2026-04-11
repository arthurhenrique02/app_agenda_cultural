"""Tests for profile read and update endpoints (US-012)."""

import pytest
from httpx import AsyncClient

from app.security.jwt import create_access_token


@pytest.fixture
async def user_with_token(async_client_with_tables: AsyncClient) -> dict:
    """Register a user and return their data plus a valid access token."""
    resp = await async_client_with_tables.post(
        "/api/auth/register",
        json={"name": "Carol", "email": "carol@example.com", "password": "pass1234"},
    )
    assert resp.status_code == 201
    user = resp.json()
    token = create_access_token(str(user["id"]))
    return {"user": user, "token": token}


# --- GET /api/users/me ---


async def test_get_profile_requires_auth(async_client_with_tables: AsyncClient) -> None:
    """GET /api/users/me returns 401 when unauthenticated."""
    resp = await async_client_with_tables.get("/api/users/me")
    assert resp.status_code == 401


async def test_get_profile_returns_user_data(
    async_client_with_tables: AsyncClient,
    user_with_token: dict,
) -> None:
    """GET /api/users/me returns the authenticated user's profile."""
    token = user_with_token["token"]
    resp = await async_client_with_tables.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "carol@example.com"
    assert data["name"] == "Carol"
    assert "hashed_password" not in data


# --- PUT /api/users/me ---


async def test_update_profile_requires_auth(
    async_client_with_tables: AsyncClient,
) -> None:
    """PUT /api/users/me returns 401 when unauthenticated."""
    resp = await async_client_with_tables.put(
        "/api/users/me",
        json={"name": "New Name"},
    )
    assert resp.status_code == 401


async def test_update_profile_name(
    async_client_with_tables: AsyncClient,
    user_with_token: dict,
) -> None:
    """Authenticated user can update their name."""
    token = user_with_token["token"]
    resp = await async_client_with_tables.put(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Carol Updated"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Carol Updated"
    assert data["email"] == "carol@example.com"


async def test_update_profile_email(
    async_client_with_tables: AsyncClient,
    user_with_token: dict,
) -> None:
    """Authenticated user can update their email."""
    token = user_with_token["token"]
    resp = await async_client_with_tables.put(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "carol.new@example.com"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "carol.new@example.com"
    assert data["name"] == "Carol"


async def test_update_profile_name_and_email(
    async_client_with_tables: AsyncClient,
    user_with_token: dict,
) -> None:
    """Authenticated user can update both name and email at once."""
    token = user_with_token["token"]
    resp = await async_client_with_tables.put(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Updated Name", "email": "updated@example.com"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Updated Name"
    assert data["email"] == "updated@example.com"


async def test_update_profile_does_not_expose_password_hash(
    async_client_with_tables: AsyncClient,
    user_with_token: dict,
) -> None:
    """PUT /api/users/me response never includes hashed_password."""
    token = user_with_token["token"]
    resp = await async_client_with_tables.put(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Safe"},
    )
    assert resp.status_code == 200
    assert "hashed_password" not in resp.json()


async def test_update_profile_duplicate_email_returns_400(
    async_client_with_tables: AsyncClient,
    user_with_token: dict,
) -> None:
    """PUT /api/users/me returns 400 when the new email is already taken."""
    # Register a second user
    await async_client_with_tables.post(
        "/api/auth/register",
        json={"name": "Dave", "email": "dave@example.com", "password": "pass1234"},
    )
    token = user_with_token["token"]
    resp = await async_client_with_tables.put(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "dave@example.com"},
    )
    assert resp.status_code == 400
