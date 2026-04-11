"""Tests for password hashing utilities."""

from app.security.password import hash_password, verify_password


def test_hash_password_returns_string():
    hashed = hash_password("mysecretpassword")
    assert isinstance(hashed, str)


def test_hash_password_not_equal_to_plain():
    plain = "mysecretpassword"
    hashed = hash_password(plain)
    assert hashed != plain


def test_hash_password_different_each_time():
    plain = "mysecretpassword"
    hashed1 = hash_password(plain)
    hashed2 = hash_password(plain)
    assert hashed1 != hashed2


def test_verify_password_correct():
    plain = "mysecretpassword"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True


def test_verify_password_wrong():
    plain = "mysecretpassword"
    hashed = hash_password(plain)
    assert verify_password("wrongpassword", hashed) is False


def test_verify_password_empty_fails():
    hashed = hash_password("somepassword")
    assert verify_password("", hashed) is False


def test_hash_is_argon2_format():
    hashed = hash_password("password123")
    assert hashed.startswith("$argon2")
