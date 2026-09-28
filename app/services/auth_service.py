from fastapi import status, Request, Response
from beanie import PydanticObjectId
from beanie.operators import Or
from pydantic import EmailStr
from datetime import datetime, timezone, timedelta
from app.core.settings import settings
from app.security.password import verify_password, get_dummy_password
from app.exceptions.custom_exception import AppException
from app.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    new_jti,
    COOKIE_BASE,
    ACCESS_TOKEN,
    REFRESH_TOKEN,
)
from app.models import User, RefreshToken
from app.schemas.user_schema import UserDetailsResponse


class AuthService:
    async def authenticate(self, username: EmailStr | str, password: str):
        user = await User.find_one(
            Or(User.email == username, User.phone == username), User.is_active == True
        )
        password_hash = user.hashed_password if user else get_dummy_password()
        if not user or not verify_password(password, password_hash):
            raise AppException(
                "Invalid username or password", status.HTTP_401_UNAUTHORIZED
            )
        return user

    async def login(self, response: Response, login_data):
        data = login_data.model_dump()
        user = await self.authenticate(data.get("username"), data.get("password"))

        jti = new_jti()
        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id, jti)

        await RefreshToken(
            jti=jti,
            user=user,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_TIMEDELTA),
        ).create()

        response.set_cookie(ACCESS_TOKEN, access, **COOKIE_BASE)
        response.set_cookie(REFRESH_TOKEN, refresh, **COOKIE_BASE)

        return {"message": "Login successful"}

    async def refresh(self, request: Request, response: Response):
        refresh_token = request.cookies.get(REFRESH_TOKEN)

        if not refresh_token:
            raise AppException("Invalid refresh token", status.HTTP_401_UNAUTHORIZED)

        payload = decode_token(refresh_token)
        if payload["type"] != "refresh":
            raise AppException(
                "Provided token is not a refresh token", status.HTTP_401_UNAUTHORIZED
            )

        old_token = await RefreshToken.find_one(
            RefreshToken.jti == payload["jti"], RefreshToken.revoked == False
        )
        if not old_token:
            raise AppException("Refresh token is expired or revoked")

        # revoke token
        await old_token.set({RefreshToken.revoked: True})

        jti = new_jti()
        await RefreshToken(
            jti=jti,
            user=payload["sub"],
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_TIMEDELTA),
        ).create()

        new_access = create_access_token(payload["sub"])
        new_refresh = create_refresh_token(payload["sub"], jti)

        response.set_cookie(ACCESS_TOKEN, new_access, **COOKIE_BASE)
        response.set_cookie(REFRESH_TOKEN, new_refresh, **COOKIE_BASE)

        return {"message": "Tokens refreshed successfully"}

    async def logout(self, request: Request, response: Response):
        refresh_token = request.cookies.get(REFRESH_TOKEN)
        payload = decode_token(refresh_token)

        user = await User.find_one(User.id == payload["sub"])
        if not user:
            return AppException("User not found", status.HTTP_404_NOT_FOUND)

        await RefreshToken.find_one(RefreshToken.jti == payload["jti"]).set(
            {RefreshToken.revoked: True}
        )

        response.delete_cookie(ACCESS_TOKEN, path="/")
        response.delete_cookie(REFRESH_TOKEN, path="/")

        return {"message": "Logged out"}

    async def get_profile(self, user_id: PydanticObjectId):
        current_user = await User.find_one(
            User.id == user_id, User.is_active == True, fetch_links=True
        )
        if not current_user:
            raise AppException("User not found.", status.HTTP_404_NOT_FOUND)
        return UserDetailsResponse.from_document(current_user)
