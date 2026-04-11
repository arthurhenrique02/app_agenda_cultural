"""Password hashing and verification using Argon2."""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_ph = PasswordHasher()


def hash_password(plain: str) -> str:
    """Hash a plain-text password with Argon2."""
    return _ph.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the Argon2 hashed password."""
    try:
        return _ph.verify(hashed, plain)
    except VerifyMismatchError:
        return False
