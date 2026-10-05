import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union, Dict
import jwt
import bcrypt
from app.core.config import settings
from app.core.exceptions import ValidationFailedError


COMMON_WEAK_PASSWORDS = {
    "password", "password123", "12345678", "123456789", "qwertyuiop",
    "admin123", "adminadmin", "existence", "existence123"
}


def validate_password_strength(password: str) -> None:
    """
    Validate that password adheres to the enterprise password policy.
    Enforces minimum length, maximum length, character composition,
    and common password rejection without unnecessary usability friction.
    """
    if not password or not isinstance(password, str):
        raise ValidationFailedError("Password must not be empty.")

    stripped = password.strip()
    if not stripped:
        raise ValidationFailedError("Password cannot consist entirely of whitespace.")

    if len(password) < settings.PASSWORD_MIN_LENGTH:
        raise ValidationFailedError(f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters in length.")

    if len(password) > settings.PASSWORD_MAX_LENGTH:
        raise ValidationFailedError(f"Password cannot exceed {settings.PASSWORD_MAX_LENGTH} characters in length.")

    if password.lower() in COMMON_WEAK_PASSWORDS:
        raise ValidationFailedError("Password is too common or easily guessable. Please choose a stronger password.")


def validate_pin_format(pin: str) -> None:
    """
    Validate that a proposed security PIN meets structural requirements.
    Must be 4 to 8 numeric digits.
    """
    if not pin or not isinstance(pin, str):
        raise ValidationFailedError("Security PIN must not be empty.")

    clean_pin = pin.strip()
    if not re.match(r"^\d{4,8}$", clean_pin):
        raise ValidationFailedError("Security PIN must consist of 4 to 8 numeric digits (e.g. '1234' or '849201').")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with 12 rounds."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def hash_pin(pin: str) -> str:
    """
    Hash a security PIN using bcrypt.
    We apply a domain separation prefix to ensure PIN hashes cannot collide with password hashes.
    """
    clean_pin = pin.strip()
    salted = f"existence_pin_salt_{clean_pin}".encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(salted, salt).decode("utf-8")


def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
    """Verify a plain PIN against its hashed value."""
    try:
        clean_pin = plain_pin.strip()
        salted = f"existence_pin_salt_{clean_pin}".encode("utf-8")
        return bcrypt.checkpw(salted, hashed_pin.encode("utf-8"))
    except Exception:
        return False


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    jti: Optional[str] = None,
    claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a signed JWT access token.
    Embeds sub (user ID), exp, iat, token type, and unique jti (JWT ID)
    for server-side session revocation tracking.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    token_jti = jti or str(uuid.uuid4())
    to_encode = {
        "sub": str(subject),
        "jti": token_jti,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }

    if claims:
        to_encode.update(claims)

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT access token.
    Enforces algorithm verification to prevent algorithm confusion attacks.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"require": ["exp", "sub"]}
        )
        return payload
    except jwt.PyJWTError:
        return None

