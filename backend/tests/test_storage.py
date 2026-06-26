"""Tests for SeaweedFS/S3-compatible storage service - US-035."""

from unittest.mock import MagicMock, patch

import pytest

from app.services.storage import StorageService


@pytest.fixture
def storage() -> StorageService:
    """Create a StorageService instance with test config."""
    return StorageService(
        endpoint="http://localhost:8333",
        public_url="http://localhost:8333",
        access_key="testaccesskey",
        secret_key="testsecretkey",
        bucket="test-bucket",
    )


def test_storage_service_initializes_with_config() -> None:
    """StorageService stores endpoint, bucket, and credentials."""
    svc = StorageService(
        endpoint="http://s3:9000",
        public_url="http://localhost:9000",
        access_key="mykey",
        secret_key="mysecret",
        bucket="my-bucket",
    )
    assert svc.bucket == "my-bucket"
    assert svc.public_url == "http://localhost:9000"


def test_storage_service_creates_s3_client() -> None:
    """StorageService creates a boto3 S3 client pointing at the configured endpoint."""
    svc = StorageService(
        endpoint="http://localhost:8333",
        public_url="http://localhost:8333",
        access_key="ak",
        secret_key="sk",
        bucket="b",
    )
    assert svc.client is not None


@patch("app.services.storage.boto3")
def test_storage_service_passes_endpoint_to_boto3(mock_boto3: MagicMock) -> None:
    """StorageService passes the endpoint_url to boto3 client constructor."""
    StorageService(
        endpoint="http://seaweed:8333",
        public_url="http://localhost:8333",
        access_key="ak",
        secret_key="sk",
        bucket="mybucket",
    )
    mock_boto3.client.assert_called_once_with(
        "s3",
        endpoint_url="http://seaweed:8333",
        aws_access_key_id="ak",
        aws_secret_access_key="sk",
    )


@patch("app.services.storage.boto3")
def test_upload_file_calls_put_object(mock_boto3: MagicMock) -> None:
    """upload_file sends file data to S3 with correct key and content type."""
    mock_client = MagicMock()
    mock_boto3.client.return_value = mock_client

    svc = StorageService(
        endpoint="http://seaweed:8333",
        public_url="http://localhost:8333",
        access_key="ak",
        secret_key="sk",
        bucket="test-bucket",
    )

    file_data = b"fake-image-bytes"
    url = svc.upload_file(
        file_data=file_data,
        key="images/abc123.jpg",
        content_type="image/jpeg",
    )

    mock_client.put_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="images/abc123.jpg",
        Body=file_data,
        ContentType="image/jpeg",
    )
    assert url == "http://localhost:8333/test-bucket/images/abc123.jpg"


@patch("app.services.storage.boto3")
def test_delete_file_calls_delete_object(mock_boto3: MagicMock) -> None:
    """delete_file removes a file from S3 by key."""
    mock_client = MagicMock()
    mock_boto3.client.return_value = mock_client

    svc = StorageService(
        endpoint="http://localhost:8333",
        public_url="http://localhost:8333",
        access_key="ak",
        secret_key="sk",
        bucket="test-bucket",
    )

    svc.delete_file(key="images/abc123.jpg")

    mock_client.delete_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="images/abc123.jpg",
    )


@patch("app.services.storage.boto3")
def test_upload_returns_public_url(mock_boto3: MagicMock) -> None:
    """upload_file returns the public URL combining endpoint, bucket, and key."""
    mock_boto3.client.return_value = MagicMock()

    svc = StorageService(
        endpoint="http://seaweed:8333",
        public_url="http://localhost:8333",
        access_key="ak",
        secret_key="sk",
        bucket="agenda-cultural",
    )

    url = svc.upload_file(
        file_data=b"data",
        key="events/photo.png",
        content_type="image/png",
    )

    assert url == "http://localhost:8333/agenda-cultural/events/photo.png"


def test_default_storage_instance_uses_settings() -> None:
    """Module-level get_storage_service creates instance from app settings."""
    from app.services.storage import get_storage_service

    svc = get_storage_service()
    assert isinstance(svc, StorageService)
