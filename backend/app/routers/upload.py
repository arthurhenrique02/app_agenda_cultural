"""Image upload endpoint."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.storage import get_storage_service

router = APIRouter(prefix="/api/upload", tags=["upload"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/image")
async def upload_image(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Upload an image file and return its public URL.

    Accepts jpg, png, webp. Max size 5MB.
    """
    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: jpg, png, webp.",
        )

    # Read file and validate size
    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit.",
        )

    # Generate unique key
    ext = _get_extension(file.content_type)
    key = f"events/{uuid.uuid4().hex}.{ext}"

    # Upload to storage
    storage = get_storage_service()
    url = storage.upload_file(file_data=data, key=key, content_type=file.content_type)

    return {"url": url}


def _get_extension(content_type: str) -> str:
    """Map content type to file extension."""
    mapping = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
    }
    return mapping.get(content_type, "bin")
