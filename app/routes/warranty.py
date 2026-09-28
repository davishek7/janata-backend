from fastapi import APIRouter, Depends, Query
from beanie import PydanticObjectId
from app.security.dependencies import get_current_user_id
from app.services import WarrantyService


router = APIRouter()


@router.get("/search")
async def check_warranty(
    serial_number=Query(""),
    user_id: PydanticObjectId = Depends(get_current_user_id),
    warranty_service: WarrantyService = Depends(),
):
    return await warranty_service.search_warranty(serial_number)
