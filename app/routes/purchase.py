from fastapi import APIRouter, Depends, Query
from typing import List
from beanie import PydanticObjectId
from app.security.dependencies import get_current_user_id
from app.services import PurchaseService
from app.schemas.purchase_schema import PurchaseCreate, PurchaseQueryParams


router = APIRouter()


@router.post("/vendor/{vendor_id}/purchase")
async def create_purchase(
    purchase_create_schema: PurchaseCreate,
    vendor_id: PydanticObjectId,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    purchase_service: PurchaseService = Depends(),
):
    return await purchase_service.create_purchase(purchase_create_schema, vendor_id)


@router.get("/vendor/{vendor_id}/purchase")
async def get_purchases(
    vendor_id: PydanticObjectId,
    params: PurchaseQueryParams = Depends(),
    user_id: PydanticObjectId = Depends(get_current_user_id),
    purchase_service: PurchaseService = Depends(),
):
    return await purchase_service.get_purchases(PydanticObjectId(vendor_id), params)


@router.get("/purchase/{purchase_id}")
async def get_purchases(
    purchase_id: PydanticObjectId,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    purchase_service: PurchaseService = Depends(),
):
    return await purchase_service.get_purchase(purchase_id)
