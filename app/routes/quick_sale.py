from fastapi import APIRouter, Depends
from beanie import PydanticObjectId
from app.services import QuickSaleService
from app.security.dependencies import get_current_user_id
from app.schemas.quick_sale_schema import QuickSaleCreate, QuickSaleQueryParams


router = APIRouter()


@router.post("/")
async def create_sale(
    quick_sale_create: QuickSaleCreate,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    quick_sale_service: QuickSaleService = Depends(),
):
    return await quick_sale_service.create_sale(quick_sale_create)


@router.get("/")
async def get_sales(
    params: QuickSaleQueryParams = Depends(),
    user_id: PydanticObjectId = Depends(get_current_user_id),
    quick_sale_service: QuickSaleService = Depends(),
):
    return await quick_sale_service.get_sales(params)


@router.get("/{sale_id}")
async def get_sale(
    sale_id: PydanticObjectId,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    quick_sale_service: QuickSaleService = Depends(),
):
    return await quick_sale_service.get_sale(sale_id)
