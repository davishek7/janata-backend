from fastapi import APIRouter, Depends
from beanie import PydanticObjectId
from app.security.dependencies import get_current_user_id
from app.services import ScrapSaleService
from app.schemas.scrap_sale_schema import ScrapSaleCreate

router = APIRouter()


@router.post("/")
async def create_sale(
    sale_create: ScrapSaleCreate,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    scrap_sale_service: ScrapSaleService = Depends(),
):
    return await scrap_sale_service.create_sale(sale_create)
