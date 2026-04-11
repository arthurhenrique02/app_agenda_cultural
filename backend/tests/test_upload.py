"""Tests for image upload endpoint (US-036)."""

from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app import database as db_module
from app.main import app
from app.models import Base
from app.models.user import User
from app.security.jwt import create_access_token
from app.security.password import hash_password

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


async def _setup_user(factory) -> str:
    """Create a test user and return an access token."""
    async with factory() as session:
        user = User(
            name="Uploader",
            email="uploader@test.com",
            hashed_password=hash_password("pass123"),
            role="user",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return create_access_token(str(user.id))


@pytest.fixture
async def client_with_auth():
    """Provide client and auth token with tables created."""
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    test_factory = async_sessionmaker(test_engine, expire_on_commit=False)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    original_factory = db_module.AsyncSessionLocal
    db_module.AsyncSessionLocal = test_factory

    token = await _setup_user(test_factory)

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            yield client, token
    finally:
        db_module.AsyncSessionLocal = original_factory
        await test_engine.dispose()


@patch("app.routers.upload.get_storage_service")
async def test_upload_image_success(mock_get_storage, client_with_auth):
    """Successful upload returns public URL."""
    client, token = client_with_auth
    mock_service = MagicMock()
    mock_service.upload_file.return_value = "http://storage/bucket/img.png"
    mock_get_storage.return_value = mock_service

    file_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    response = await client.post(
        "/api/upload/image",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.png", file_content, "image/png")},
    )

    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert data["url"] == "http://storage/bucket/img.png"
    mock_service.upload_file.assert_called_once()


@patch("app.routers.upload.get_storage_service")
async def test_upload_image_jpg(mock_get_storage, client_with_auth):
    """JPEG upload is accepted."""
    client, token = client_with_auth
    mock_service = MagicMock()
    mock_service.upload_file.return_value = "http://storage/bucket/img.jpg"
    mock_get_storage.return_value = mock_service

    file_content = b"\xff\xd8\xff\xe0" + b"\x00" * 100
    response = await client.post(
        "/api/upload/image",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.jpg", file_content, "image/jpeg")},
    )

    assert response.status_code == 200


@patch("app.routers.upload.get_storage_service")
async def test_upload_image_webp(mock_get_storage, client_with_auth):
    """WebP upload is accepted."""
    client, token = client_with_auth
    mock_service = MagicMock()
    mock_service.upload_file.return_value = "http://storage/bucket/img.webp"
    mock_get_storage.return_value = mock_service

    file_content = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 100
    response = await client.post(
        "/api/upload/image",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.webp", file_content, "image/webp")},
    )

    assert response.status_code == 200


async def test_upload_requires_auth(client_with_auth):
    """Upload without auth returns 401."""
    client, _ = client_with_auth
    file_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    response = await client.post(
        "/api/upload/image",
        files={"file": ("test.png", file_content, "image/png")},
    )

    assert response.status_code == 401


async def test_upload_rejects_invalid_type(client_with_auth):
    """Upload with unsupported file type returns 400."""
    client, token = client_with_auth
    file_content = b"%PDF-1.4 fake pdf content"
    response = await client.post(
        "/api/upload/image",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.pdf", file_content, "application/pdf")},
    )

    assert response.status_code == 400
    assert "type" in response.json()["detail"].lower()


async def test_upload_rejects_large_file(client_with_auth):
    """Upload over 5MB returns 400."""
    client, token = client_with_auth
    # 5MB + 1 byte
    file_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * (5 * 1024 * 1024 + 1)
    response = await client.post(
        "/api/upload/image",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("big.png", file_content, "image/png")},
    )

    assert response.status_code == 400
    assert "size" in response.json()["detail"].lower()
