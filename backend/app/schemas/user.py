"""User-related Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserResponse(BaseModel):
    """Public user representation — never includes hashed_password."""

    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    """Fields that a user is allowed to update on their own profile."""

    name: str | None = None
    email: EmailStr | None = None
