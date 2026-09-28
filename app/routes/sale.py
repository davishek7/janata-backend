from fastapi import APIRouter, Depends, Query
from beanie import PydanticObjectId
from app.services import SaleService
from app.schemas.sale_schema import SaleCreate, SaleQueryParams
from app.security.dependencies import get_current_user_id


router = APIRouter()


@router.post("/")
async def create_sale(
    sale_create_schema: SaleCreate,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    sale_service: SaleService = Depends(),
):
    return await sale_service.create_sale(sale_create_schema)


@router.get("/")
async def get_sales(
    params: SaleQueryParams = Depends(),
    user_id: PydanticObjectId = Depends(get_current_user_id),
    sale_service: SaleService = Depends(),
):
    return await sale_service.get_sales(params)


@router.get("/{sale_id}")
async def get_sale(
    sale_id: PydanticObjectId,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    sale_service: SaleService = Depends(),
):
    return await sale_service.get_sale(PydanticObjectId(sale_id))
