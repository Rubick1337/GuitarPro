"""Authentication helpers for the FastAPI server."""
from datetime import datetime, timedelta
from typing import Any, Dict

import jwt
from passlib.context import CryptContext

ALGORITHM = "HS256"
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain password using passlib."""
    return _pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Validate a password against the stored hash."""
    return _pwd_context.verify(password, hashed_password)


def create_access_token(*, data: Dict[str, Any], secret_key: str, expires_delta: timedelta) -> str:
    """Create a signed JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str, secret_key: str) -> Dict[str, Any]:
    """Decode a JWT token and return its payload."""
    return jwt.decode(token, secret_key, algorithms=[ALGORITHM])
