from fastapi import APIRouter, Depends
from beanie import PydanticObjectId
from app.security.dependencies import get_current_user_id
from app.services import ScrapPurchaseService
from app.schemas.scrap_purchase_schema import (
    ScrapPurchaseCreate,
    ScrapPurchaseQueryParams,
)

router = APIRouter()


@router.post("/")
async def create_purchase(
    purchase_create: ScrapPurchaseCreate,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    scrap_purchase_service: ScrapPurchaseService = Depends(),
):
    return await scrap_purchase_service.create_purchase(purchase_create)


@router.get("/")
async def get_purchases(
    params: ScrapPurchaseQueryParams = Depends(),
    user_id: PydanticObjectId = Depends(get_current_user_id),
    scrap_purchase_service: ScrapPurchaseService = Depends(),
):
    return await scrap_purchase_service.get_purchases(params)


@router.get("/{purchase_id}")
async def get_purchase(
    purchase_id: PydanticObjectId,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    scrap_purchase_service: ScrapPurchaseService = Depends(),
):
    scrap_purchase_service.get_purchase(purchase_id)
