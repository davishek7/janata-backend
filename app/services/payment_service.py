from fastapi import status
import re
from beanie import PydanticObjectId
from beanie.operators import Or
from decimal import Decimal
from pymongo.asynchronous.client_session import AsyncClientSession
from app.core.database import transaction
from app.models import Payment, Invoice, QuickSale, ScrapPurchase, ScrapSale
from app.schemas.payment_schema import (
    PaymentQueryParams,
    PaymentResponse,
    PaymentCreate,
)
from app.enums.PaymentReferenceType import PaymentReferenceType
from app.enums.PaymentStatus import PaymentStatus
from app.schemas.common.pagination_schema import Pagination, PaginatedResponse
from app.utils.pagination import paginate
from app.utils.responses import success_response
from app.exceptions.custom_exception import AppException


PAYMENT_REFERENCE_MODELS = {
    PaymentReferenceType.QUICK_SALE: QuickSale,
    PaymentReferenceType.INVOICE: Invoice,
    PaymentReferenceType.SCRAP_SALE: ScrapSale,
    PaymentReferenceType.SCRAP_PURCHASE: ScrapPurchase,
}


class PaymentService:
    async def create_payment(self, payment_create: PaymentCreate):
        async with transaction() as session:
            return await self._create_payment(payment_create, session)

    async def _create_payment(
        self, payment_create: PaymentCreate, session: AsyncClientSession | None = None
    ):
        payment_data = payment_create.model_dump(exclude_unset=True)
        payment = Payment(**payment_data)
        await payment.insert(session=session)
        await self._recalculate_payment_status(
            reference_type=payment.reference_type,
            reference_id=payment.reference_id,
            amount=payment_create.amount,
            session=session,
        )
        return success_response(
            "Payment created successfully.", status.HTTP_201_CREATED
        )

    async def get_payments(self, params: PaymentQueryParams):
        conditions = []
        if params.search:
            search = re.escape(params.search.strip())

            conditions.append(
                Or(
                    {"reference_id": {"$regex": search, "$options": "i"}},
                )
            )

        if params.reference_type:
            conditions.append(Payment.reference_type == params.reference_type)

        if params.direction:
            conditions.append(Payment.direction == params.direction)

        if params.payment_mode:
            conditions.append(Payment.payment_mode == params.payment_mode)

        query = Payment.find(*conditions, Payment.is_active == True).sort(
            -Payment.payment_date
        )

        payments, total = await paginate(query, page=params.page, size=params.size)
        return PaginatedResponse[PaymentResponse](
            items=[PaymentResponse.from_document(payment) for payment in payments],
            pagination=Pagination.from_total(
                page=params.page, size=params.size, total=total
            ),
        )

    async def _get_payment_reference(
        self,
        reference_type: PaymentReferenceType,
        reference_id: PydanticObjectId,
        session: AsyncClientSession | None = None,
    ):
        model = PAYMENT_REFERENCE_MODELS.get(reference_type)
        if model is None:
            return None
        return await model.get(reference_id, session=session)

    async def _recalculate_payment_status(
        self,
        reference_type: PaymentReferenceType,
        reference_id: PydanticObjectId,
        amount: Decimal,
        session: AsyncClientSession | None = None,
    ):
        reference = await self._get_payment_reference(
            reference_type, reference_id, session=session
        )
        if reference is None:
            raise AppException(
                "Payment reference not found.", status.HTTP_404_NOT_FOUND
            )
        payments = await Payment.find(
            Payment.reference_type == reference_type,
            Payment.reference_id == reference_id,
            Payment.is_active == True,
            session=session,
        ).to_list()

        paid_amount = sum(
            (payment.amount for payment in payments),
            Decimal("0"),
        )

        if reference.paid_amount == reference.total_amount:
            raise AppException("Invoice is fully paid.", status.HTTP_400_BAD_REQUEST)

        new_paid_amount = reference.paid_amount + amount

        if new_paid_amount > reference.total_amount:
            raise AppException(
                "Payment exceeds invoice amount.",
                status.HTTP_400_BAD_REQUEST,
            )

        reference.paid_amount = paid_amount

        if paid_amount <= Decimal("0"):
            reference.payment_status = PaymentStatus.UNPAID
        elif paid_amount < reference.total_amount:
            reference.payment_status = PaymentStatus.PARTIAL
        else:
            reference.payment_status = PaymentStatus.PAID

        await reference.save(session=session)
