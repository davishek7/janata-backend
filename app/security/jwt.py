import jwt
from uuid import uuid4
from fastapi import status
from beanie import PydanticObjectId
from datetime import datetime, timedelta, timezone
from app.core.settings import settings
from app.exceptions.custom_exception import AppException


ACCESS_TOKEN = "janata_access_token"
REFRESH_TOKEN = "janata_refresh_token"

COOKIE_BASE = dict(
    httponly=True,
    secure=True,  # True in prod (HTTPS)
    samesite="none",
    path="/",
)


def new_jti() -> str:
    return str(uuid4())


def create_access_token(user_id: PydanticObjectId | str) -> str:
    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_TIMEDELTA),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGO)


def create_refresh_token(user_id: PydanticObjectId | str, jti: str) -> str:
    payload = {
        "sub": str(user_id),
        "jti": jti,
        "type": "refresh",
        "exp": datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_TIMEDELTA),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGO)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGO)
    except jwt.exceptions.ExpiredSignatureError:
        raise AppException("Token expired", status.HTTP_401_UNAUTHORIZED)
    except jwt.exceptions.DecodeError:
        raise AppException("Malformed token", status.HTTP_401_UNAUTHORIZED)
    except jwt.exceptions.InvalidTokenError:
        raise AppException("Invalid token", status.HTTP_401_UNAUTHORIZED)
