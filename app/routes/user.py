from fastapi import APIRouter, Depends, Query
from beanie import PydanticObjectId
from app.services import UserService
from app.security.dependencies import get_current_user_id
from app.schemas.user_schema import UserCreate, UserQueryParams


router = APIRouter()


@router.post("/")
async def create_user(
    user_create: UserCreate,
    current_user_id: PydanticObjectId = Depends(get_current_user_id),
    user_service: UserService = Depends(),
):
    return await user_service.create_user(user_create)


@router.get("/")
async def get_users(
    params: UserQueryParams = Depends(),
    current_user_id: PydanticObjectId = Depends(get_current_user_id),
    user_service: UserService = Depends(),
):
    return await user_service.get_users(params)


@router.get("/{user_id}")
async def get_user(
    user_id: PydanticObjectId,
    current_user_id: PydanticObjectId = Depends(get_current_user_id),
    user_service: UserService = Depends(),
):
    return await user_service.get_user(user_id)


@router.patch("/{user_id}")
async def deactivate_user(
    user_id: PydanticObjectId,
    current_user_id: PydanticObjectId = Depends(get_current_user_id),
    user_service: UserService = Depends(),
):
    return await user_service.deactivate_user(user_id)
