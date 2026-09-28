from fastapi import APIRouter, Depends, Query
from typing import List
from beanie import PydanticObjectId
from app.security.dependencies import get_current_user_id
from app.services import ProductService
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductQueryParams


router = APIRouter()


@router.post("/")
async def create_product(
    product_create_schema: ProductCreate,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    product_service: ProductService = Depends(),
):
    return await product_service.create_product(product_create_schema)


@router.get("/lookup")
async def product_lookup(
    user_id: PydanticObjectId = Depends(get_current_user_id),
    product_service: ProductService = Depends(),
):
    return await product_service.product_lookup()


@router.get("/")
async def get_products(
    params: ProductQueryParams = Depends(),
    user_id: PydanticObjectId = Depends(get_current_user_id),
    product_service: ProductService = Depends(),
):
    return await product_service.get_products(params)


@router.get("/{product_id}")
async def get_product(
    product_id: PydanticObjectId,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    product_service: ProductService = Depends(),
):
    return await product_service.get_product(product_id)


@router.patch("/{product_id}")
async def update_product(
    product_id: PydanticObjectId,
    product_update_schema: ProductUpdate,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    product_service: ProductService = Depends(),
):
    return await product_service.update_product(product_id, product_update_schema)


@router.get("/{product_id}/in-stock-serials")
async def get_in_stock_serials(
    product_id: PydanticObjectId,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    product_service: ProductService = Depends(),
):
    return await product_service.get_in_stock_serials(product_id)
