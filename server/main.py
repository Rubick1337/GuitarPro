"""FastAPI application providing JWT protected endpoints."""
import os
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from . import auth, schemas
from .storage import UserRepository

SECRET_KEY = os.getenv("GUITARPRO_SECRET_KEY", "change-me-in-production")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

app = FastAPI(title="GuitarPro API")
_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
_repo = UserRepository()


@app.post("/auth/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate) -> schemas.UserRead:
    """Register a new user in the in-memory store."""
    try:
        created = _repo.create(user.username, user.password)
    except ValueError as exc:  # pragma: no cover - simple branch
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return schemas.UserRead(username=created.username, created_at=created.created_at)

@app.post("/auth/login", response_model=schemas.TokenResponse)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> schemas.TokenResponse:
    """Authenticate a user and return a JWT token."""
    user = _repo.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = auth.create_access_token(
        data={"sub": user.username},
        secret_key=SECRET_KEY,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return schemas.TokenResponse(access_token=token)

def _get_current_user(token: Annotated[str, Depends(_oauth2_scheme)]) -> str:
    """Return the username embedded in the JWT token."""
    try:
        payload = auth.decode_access_token(token, secret_key=SECRET_KEY)
    except Exception as exc:  # pragma: no cover - defensive programming
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    username: str | None = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    return username

@app.get("/profile", response_model=schemas.ProfileResponse)
def read_profile(username: Annotated[str, Depends(_get_current_user)]) -> schemas.ProfileResponse:
    """Return a simple profile response for the authenticated user."""
    user = _repo.get(username)
    if not user:  # pragma: no cover - should not happen with valid tokens
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return schemas.ProfileResponse(username=user.username, joined=user.created_at, bio=user.bio)

@app.get("/health", response_model=schemas.Message)
def healthcheck() -> schemas.Message:
    """Simple endpoint for monitoring."""
    return schemas.Message(detail="ok")
