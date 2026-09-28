from fastapi import APIRouter, Depends, Query
from beanie import PydanticObjectId
from app.security.dependencies import get_current_user_id
from app.services import StaffLedgerService

router = APIRouter()


@router.get("/")
async def get_staff_ledgers(
    staff_id: PydanticObjectId,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_id: PydanticObjectId = Depends(get_current_user_id),
    staff_ledger_service: StaffLedgerService = Depends(),
):
    return await staff_ledger_service.get_staff_ledgers(staff_id, page, size)
