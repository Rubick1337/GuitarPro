"""Application state shared across screens."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AppState:
    token: Optional[str] = None
    username: Optional[str] = None
    messages: list[str] = field(default_factory=list)

    def set_credentials(self, *, token: str, username: str) -> None:
        self.token = token
        self.username = username

    def clear(self) -> None:
        self.token = None
        self.username = None
        self.messages.clear()

    def add_message(self, message: str) -> None:
        self.messages.append(message)
