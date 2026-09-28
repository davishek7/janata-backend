from fastapi import APIRouter, Depends
from typing import List
from beanie import PydanticObjectId
from app.security.dependencies import get_current_user_id
from app.services import VendorService
from app.schemas.vendor_schema import (
    VendorCreate,
    VendorUpdate,
    VendorQueryParams,
    VendorLedgerQueryParams,
)


router = APIRouter()


@router.post("/")
async def create_vendor(
    vendor_create_schema: VendorCreate,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    vendor_service: VendorService = Depends(),
):
    return await vendor_service.create_vendor(vendor_create_schema)


@router.get("/lookup")
async def vendor_lookup(
    user_id: PydanticObjectId = Depends(get_current_user_id),
    vendor_service: VendorService = Depends(),
):
    return await vendor_service.vendor_lookup()


@router.get("/")
async def get_vendors(
    params: VendorQueryParams = Depends(),
    user_id: PydanticObjectId = Depends(get_current_user_id),
    vendor_service: VendorService = Depends(),
):
    return await vendor_service.get_vendors(params)


@router.get("/{vendor_id}")
async def get_vendor(
    vendor_id: PydanticObjectId,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    vendor_service: VendorService = Depends(),
):
    return await vendor_service.get_vendor(vendor_id)


@router.get("/{vendor_id}/ledger")
async def get_vendor_ledgers(
    vendor_id: PydanticObjectId,
    params: VendorLedgerQueryParams = Depends(),
    user_id: PydanticObjectId = Depends(get_current_user_id),
    vendor_service: VendorService = Depends(),
):
    return await vendor_service.get_vendor_ledgers(vendor_id, params)
