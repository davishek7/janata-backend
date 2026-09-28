from fastapi import status, Request
from app.security.jwt import decode_token, ACCESS_TOKEN
from beanie import PydanticObjectId
from app.exceptions.custom_exception import AppException


async def get_current_user_id(request: Request) -> PydanticObjectId:
    access_token = request.cookies.get(ACCESS_TOKEN)

    if not access_token:
        raise AppException("Not authenticated", status.HTTP_401_UNAUTHORIZED)

    payload = decode_token(access_token)
    return PydanticObjectId(payload["sub"])
