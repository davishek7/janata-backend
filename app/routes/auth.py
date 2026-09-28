from fastapi import APIRouter, Depends, Request, Response
from beanie import PydanticObjectId
from app.schemas.auth_schema import LoginSchema
from app.services import AuthService
from app.security.dependencies import get_current_user_id


router = APIRouter()


@router.post("/login")
async def login(
    response: Response, login_schema: LoginSchema, auth_service: AuthService = Depends()
):
    return await auth_service.login(response, login_schema)


@router.post("/refresh")
async def refresh(
    request: Request, response: Response, auth_service: AuthService = Depends()
):
    return await auth_service.refresh(request, response)


@router.post("/logout")
async def logout(
    request: Request, response: Response, auth_service: AuthService = Depends()
):
    return await auth_service.logout(request, response)


@router.get("/me")
async def get_profile(
    user_id: PydanticObjectId = Depends(get_current_user_id),
    auth_service: AuthService = Depends(),
):
    return await auth_service.get_profile(user_id)
