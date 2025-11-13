"""In-memory storage for demonstration purposes."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

from .auth import hash_password, verify_password


@dataclass
class User:
    username: str
    password_hash: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    bio: Optional[str] = None


class UserRepository:
    """A minimal in-memory user repository."""

    def __init__(self) -> None:
        self._users: Dict[str, User] = {}

    def create(self, username: str, password: str) -> User:
        if username in self._users:
            raise ValueError("User already exists")
        user = User(username=username, password_hash=hash_password(password))
        self._users[username] = user
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self._users.get(username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def get(self, username: str) -> Optional[User]:
        return self._users.get(username)
