from fastapi import APIRouter, Depends
from beanie import PydanticObjectId
from app.services import MechanicInvoiceService
from app.security.dependencies import get_current_user_id
from app.schemas.mechanic_invoice_schema import MechanicInvoiceCreate


router = APIRouter()


@router.post("/mechanic/{mechanic_id}/invoice")
async def create_invoice(
    mechanic_id: PydanticObjectId,
    invoice_create: MechanicInvoiceCreate,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    invoice_service: MechanicInvoiceService = Depends(),
):
    return await invoice_service.create_invoice(mechanic_id, invoice_create)
