from fastapi import APIRouter, Depends
from beanie import PydanticObjectId
from app.security.dependencies import get_current_user_id
from app.services import InvoiceService
from app.schemas.invoice_schema import InvoiceQueryParams

router = APIRouter()


@router.get("/")
async def get_invoices(
    params: InvoiceQueryParams = Depends(),
    user_id: PydanticObjectId = Depends(get_current_user_id),
    invoice_service: InvoiceService = Depends(),
):
    return await invoice_service.get_invoices(params)


@router.get("/{invoice_id}")
async def get_invoice(
    invoice_id: PydanticObjectId,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    invoice_service: InvoiceService = Depends(),
):
    return await invoice_service.get_invoice(PydanticObjectId(invoice_id))
