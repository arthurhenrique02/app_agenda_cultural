"""S3-compatible storage service for SeaweedFS image uploads."""

import boto3

from app.config import settings


class StorageService:
    """Abstraction over S3-compatible object storage (SeaweedFS)."""

    def __init__(
        self,
        *,
        endpoint: str,
        public_url: str,
        access_key: str,
        secret_key: str,
        bucket: str,
    ) -> None:
        self.public_url = public_url
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    def upload_file(
        self,
        *,
        file_data: bytes,
        key: str,
        content_type: str,
    ) -> str:
        """Upload file data to S3 and return the public URL."""
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file_data,
            ContentType=content_type,
        )
        return f"{self.public_url}/{self.bucket}/{key}"

    def delete_file(self, *, key: str) -> None:
        """Delete a file from S3 by key."""
        self.client.delete_object(
            Bucket=self.bucket,
            Key=key,
        )


def get_storage_service() -> StorageService:
    """Create a StorageService instance from app settings."""
    return StorageService(
        endpoint=settings.storage_endpoint,
        public_url=settings.storage_public_url,
        access_key=settings.storage_access_key,
        secret_key=settings.storage_secret_key,
        bucket=settings.storage_bucket,
    )
