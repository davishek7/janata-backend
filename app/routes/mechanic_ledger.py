from fastapi import APIRouter, Depends, Query
from beanie import PydanticObjectId
from app.security.dependencies import get_current_user_id
from app.schemas.mechanic_schema import (
    MechanicLedgerCreate,
    ProductTakenCreate,
)
from app.services import MechanicService


router = APIRouter()


@router.post("/{mechanic_id}/ledger/add-product-taken")
async def create_product_taken(
    mechanic_id: PydanticObjectId,
    product_taken_create: ProductTakenCreate,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    mechanic_service: MechanicService = Depends(),
):
    return await mechanic_service.create_product_taken(
        mechanic_id, product_taken_create
    )


@router.post("/mechanic/{mechanic_id}/ledger")
async def create_ledger_entry(
    mechanic_id: PydanticObjectId,
    ledger_schema: MechanicLedgerCreate,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    mechanic_service: MechanicService = Depends(),
):
    return await mechanic_service.create_ledger_entry(mechanic_id, ledger_schema)


@router.get("/mechanic/{mechanic_id}/ledger")
async def get_mechanic_ledgers(
    mechanic_id: PydanticObjectId,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_id: PydanticObjectId = Depends(get_current_user_id),
    mechanic_service: MechanicService = Depends(),
):
    return await mechanic_service.get_mechanic_ledgers(mechanic_id, page, size)
