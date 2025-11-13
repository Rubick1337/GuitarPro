"""HTTP client for interacting with the FastAPI backend."""
from __future__ import annotations

from typing import Any, Dict

import requests


class APIClient:
    """Minimal wrapper around the REST API."""

    def __init__(self, *, base_url: str | None = None) -> None:
        self.base_url = base_url or "http://127.0.0.1:8000"

    def register(self, *, username: str, password: str) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/auth/register",
            json={"username": username, "password": password},
            timeout=5,
        )
        response.raise_for_status()
        return response.json()

    def login(self, *, username: str, password: str) -> str:
        response = requests.post(
            f"{self.base_url}/auth/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
        return data["access_token"]

    def get_profile(self, *, token: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/profile",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
