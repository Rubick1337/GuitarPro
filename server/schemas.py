"""Pydantic schemas for request/response bodies."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserRead(UserBase):
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(UserBase):
    password: str


class Message(BaseModel):
    detail: str


class ProfileResponse(BaseModel):
    username: str
    joined: datetime
    bio: Optional[str] = None
