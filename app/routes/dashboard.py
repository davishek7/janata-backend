from fastapi import APIRouter, Depends
from beanie import PydanticObjectId
from app.security.dependencies import get_current_user_id
from app.services import DashboardService


router = APIRouter()


@router.get("/")
async def get_dashboard(
    user_id: PydanticObjectId = Depends(get_current_user_id),
    dashboard_service: DashboardService = Depends(),
):
    return await dashboard_service.get_dashboard()
