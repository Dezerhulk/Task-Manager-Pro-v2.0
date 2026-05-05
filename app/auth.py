"""Authentication and authorization utilities."""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from pydantic import BaseModel

from .config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: int  # user_id
    exp: datetime
    type: str = "access"  # access or refresh


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    if expires_delta is None:
        expires_delta = settings.access_token_expire

    expire = datetime.utcnow() + expires_delta
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
    }

    encoded_jwt = jwt.encode(
        payload, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def create_refresh_token(user_id: int) -> str:
    """Create JWT refresh token."""
    expire = datetime.utcnow() + settings.refresh_token_expire
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }

    encoded_jwt = jwt.encode(
        payload, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[int]:
    """Verify JWT token and return user_id."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: int = int(payload.get("sub"))
        token_type_claim: str = payload.get("type", "access")

        if token_type_claim != token_type:
            return None

        return user_id
    except (JWTError, ValueError):
        return None


async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> int:
    """Dependency to get current user from token."""
    token = credentials.credentials

    user_id = verify_token(token, token_type="access")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def get_current_user_optional(
    credentials: Optional[HTTPAuthCredentials] = Depends(security)
) -> Optional[int]:
    """Optional dependency to get current user."""
    if credentials is None:
        return None

    user_id = verify_token(credentials.credentials, token_type="access")
    return user_id
