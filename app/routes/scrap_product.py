from fastapi import APIRouter, Depends, Query
from typing import List
from beanie import PydanticObjectId
from app.security.dependencies import get_current_user_id
from app.services import ScrapProductService
from app.schemas.scrap_product_schema import ScrapProductCreate, ScrapProductQueryParams


router = APIRouter()


@router.post("/")
async def create_scrap_product(
    scrap_product_schema: ScrapProductCreate,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    scrap_product_service: ScrapProductService = Depends(),
):
    return await scrap_product_service.create_scrap_product(scrap_product_schema)


@router.get("/lookup")
async def scrap_product_lookup(
    user_id: PydanticObjectId = Depends(get_current_user_id),
    scrap_product_service: ScrapProductService = Depends(),
):
    return await scrap_product_service.scrap_product_lookup()


@router.get("/")
async def get_scrap_products(
    params: ScrapProductQueryParams = Depends(),
    user_id: PydanticObjectId = Depends(get_current_user_id),
    scrap_product_service: ScrapProductService = Depends(),
):
    return await scrap_product_service.get_scrap_products(params)


@router.get("/{scrap_product_id}")
async def get_scrap_product(
    scrap_product_id: PydanticObjectId,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    scrap_product_service: ScrapProductService = Depends(),
):
    return await scrap_product_service.get_scrap_product(scrap_product_id)
