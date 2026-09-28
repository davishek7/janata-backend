from fastapi import APIRouter, Depends
from beanie import PydanticObjectId
from app.security.dependencies import get_current_user_id
from app.services import PaymentService
from app.schemas.payment_schema import PaymentQueryParams, PaymentCreate

router = APIRouter()


@router.post("/")
async def create_payment(
    payment_create: PaymentCreate,
    user_id: PydanticObjectId = Depends(get_current_user_id),
    payment_service: PaymentService = Depends(),
):
    return await payment_service.create_payment(payment_create)


@router.get("/")
async def get_payments(
    params: PaymentQueryParams = Depends(),
    user_id: PydanticObjectId = Depends(get_current_user_id),
    payment_service: PaymentService = Depends(),
):
    return await payment_service.get_payments(params)
