"""Tests for POST /api/auth/refresh endpoint (US-010)."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.config import settings
from app.security.jwt import ALGORITHM, create_refresh_token


def _make_token(payload: dict) -> str:
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


@pytest.mark.asyncio
async def test_refresh_returns_new_access_token(async_client_with_tables):
    """Valid refresh token returns a new access token."""
    # Register + login to get tokens
    await async_client_with_tables.post(
        "/api/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "secret123"},
    )
    login_resp = await async_client_with_tables.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "secret123"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    resp = await async_client_with_tables.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_returns_valid_jwt(async_client_with_tables):
    """The returned access token is a valid JWT with correct claims."""
    await async_client_with_tables.post(
        "/api/auth/register",
        json={"name": "Bob", "email": "bob@example.com", "password": "secret123"},
    )
    login_resp = await async_client_with_tables.post(
        "/api/auth/login",
        json={"email": "bob@example.com", "password": "secret123"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    resp = await async_client_with_tables.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    access_token = resp.json()["access_token"]
    payload = jwt.decode(access_token, settings.secret_key, algorithms=[ALGORITHM])
    assert payload["token_type"] == "access"
    assert "sub" in payload


@pytest.mark.asyncio
async def test_refresh_with_invalid_token_returns_401(async_client_with_tables):
    """Garbage token returns 401."""
    resp = await async_client_with_tables.post(
        "/api/auth/refresh",
        json={"refresh_token": "not.a.valid.token"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_with_access_token_returns_401(async_client_with_tables):
    """Using an access token as a refresh token returns 401."""
    await async_client_with_tables.post(
        "/api/auth/register",
        json={"name": "Carol", "email": "carol@example.com", "password": "secret123"},
    )
    login_resp = await async_client_with_tables.post(
        "/api/auth/login",
        json={"email": "carol@example.com", "password": "secret123"},
    )
    access_token = login_resp.json()["access_token"]

    resp = await async_client_with_tables.post(
        "/api/auth/refresh",
        json={"refresh_token": access_token},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_with_expired_token_returns_401(async_client_with_tables):
    """Expired refresh token returns 401."""
    expire = datetime.now(UTC) - timedelta(seconds=1)
    token = _make_token({"sub": "999", "exp": expire, "token_type": "refresh"})

    resp = await async_client_with_tables.post(
        "/api/auth/refresh",
        json={"refresh_token": token},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_with_nonexistent_user_returns_401(async_client_with_tables):
    """Refresh token for a user that doesn't exist returns 401."""
    token = create_refresh_token("99999")

    resp = await async_client_with_tables.post(
        "/api/auth/refresh",
        json={"refresh_token": token},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_missing_body_returns_422(async_client_with_tables):
    """Missing body returns 422 validation error."""
    resp = await async_client_with_tables.post("/api/auth/refresh", json={})
    assert resp.status_code == 422
