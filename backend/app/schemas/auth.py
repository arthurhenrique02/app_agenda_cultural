"""Auth-related Pydantic schemas."""

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """Payload for POST /api/auth/register."""

    name: str
    email: EmailStr
    password: str
