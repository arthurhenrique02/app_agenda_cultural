"""Tests for POST /api/auth/login endpoint."""

import pytest
from httpx import AsyncClient


@pytest.fixture
async def registered_user(async_client_with_tables: AsyncClient) -> dict:
    """Register a user and return the credentials used."""
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "secret123",
    }
    resp = await async_client_with_tables.post("/api/auth/register", json=payload)
    assert resp.status_code == 201
    return payload


def _login_body(user: dict) -> dict:
    return {"email": user["email"], "password": user["password"]}


async def test_login_returns_access_and_refresh_tokens(
    async_client_with_tables: AsyncClient, registered_user: dict
) -> None:
    """Successful login returns both access and refresh tokens."""
    resp = await async_client_with_tables.post(
        "/api/auth/login",
        json=_login_body(registered_user),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_login_invalid_password_returns_401(
    async_client_with_tables: AsyncClient, registered_user: dict
) -> None:
    """Wrong password returns 401."""
    resp = await async_client_with_tables.post(
        "/api/auth/login",
        json={"email": registered_user["email"], "password": "wrongpassword"},
    )
    assert resp.status_code == 401


async def test_login_unknown_email_returns_401(
    async_client_with_tables: AsyncClient,
) -> None:
    """Non-existent email returns 401."""
    resp = await async_client_with_tables.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "anypassword"},
    )
    assert resp.status_code == 401


async def test_access_token_is_valid_jwt(
    async_client_with_tables: AsyncClient, registered_user: dict
) -> None:
    """Access token can be decoded as a valid JWT with correct claims."""
    import jwt as pyjwt

    from app.config import settings

    resp = await async_client_with_tables.post(
        "/api/auth/login",
        json=_login_body(registered_user),
    )
    assert resp.status_code == 200
    access_token = resp.json()["access_token"]

    payload = pyjwt.decode(access_token, settings.secret_key, algorithms=["HS256"])
    assert payload["token_type"] == "access"
    assert "sub" in payload
    assert "exp" in payload


async def test_refresh_token_is_valid_jwt(
    async_client_with_tables: AsyncClient, registered_user: dict
) -> None:
    """Refresh token can be decoded and has correct token_type claim."""
    import jwt as pyjwt

    from app.config import settings

    resp = await async_client_with_tables.post(
        "/api/auth/login",
        json=_login_body(registered_user),
    )
    assert resp.status_code == 200
    refresh_token = resp.json()["refresh_token"]

    payload = pyjwt.decode(refresh_token, settings.secret_key, algorithms=["HS256"])
    assert payload["token_type"] == "refresh"
    assert "sub" in payload
    assert "exp" in payload


async def test_access_token_expiry_is_15_minutes(
    async_client_with_tables: AsyncClient, registered_user: dict
) -> None:
    """Access token expires approximately 15 minutes from now."""
    import time

    import jwt as pyjwt

    from app.config import settings

    before = int(time.time())
    resp = await async_client_with_tables.post(
        "/api/auth/login",
        json=_login_body(registered_user),
    )
    assert resp.status_code == 200
    access_token = resp.json()["access_token"]

    payload = pyjwt.decode(access_token, settings.secret_key, algorithms=["HS256"])
    exp = payload["exp"]
    expected_exp = before + 15 * 60
    # Allow a small margin (±5 seconds)
    assert abs(exp - expected_exp) < 5


async def test_refresh_token_expiry_is_7_days(
    async_client_with_tables: AsyncClient, registered_user: dict
) -> None:
    """Refresh token expires approximately 7 days from now."""
    import time

    import jwt as pyjwt

    from app.config import settings

    before = int(time.time())
    resp = await async_client_with_tables.post(
        "/api/auth/login",
        json=_login_body(registered_user),
    )
    assert resp.status_code == 200
    refresh_token = resp.json()["refresh_token"]

    payload = pyjwt.decode(refresh_token, settings.secret_key, algorithms=["HS256"])
    exp = payload["exp"]
    expected_exp = before + 7 * 24 * 60 * 60
    # Allow a small margin (±5 seconds)
    assert abs(exp - expected_exp) < 5
