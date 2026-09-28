from fastapi import APIRouter, Depends, Query
from beanie import PydanticObjectId
from app.security.dependencies import get_current_user_id
from app.schemas.mechanic_schema import MechanicCreate, MechanicQueryParams
from app.services import MechanicService


router = APIRouter()


@router.post("/")
async def create_mechanic(
    mechanic_create: MechanicCreate,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    mechanic_service: MechanicService = Depends(),
):
    return await mechanic_service.create_mechanic(mechanic_create)


@router.get("/")
async def get_mechanics(
    params: MechanicQueryParams = Depends(),
    user_id: PydanticObjectId = Depends(get_current_user_id),
    mechanic_service: MechanicService = Depends(),
):
    return await mechanic_service.get_mechanics(params)


@router.get("/{mechanic_id}")
async def get_mechanic(
    mechanic_id: PydanticObjectId,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    mechanic_service: MechanicService = Depends(),
):
    return await mechanic_service.get_mechanic(mechanic_id)


@router.patch("/{mechanic_id}")
async def deactivate_mechanic(
    mechanic_id: PydanticObjectId,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    mechanic_service: MechanicService = Depends(),
):
    return await mechanic_service.deactivate_mechanic(mechanic_id)
