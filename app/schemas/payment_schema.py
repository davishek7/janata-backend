from pydantic import BaseModel, Field
from beanie import PydanticObjectId
from decimal import Decimal
from datetime import datetime
from app.models import Payment, MechanicInvoicePayment
from app.enums.PaymentMode import PaymentMode
from app.enums.PaymentReferenceType import PaymentReferenceType
from app.enums.PaymentDirection import PaymentDirection
from .common.query_params import PaginationQueryParams, SearchQueryParams


class PaymentQueryParams(PaginationQueryParams, SearchQueryParams):
    reference_type: PaymentReferenceType | None = None
    direction: PaymentDirection | None = None
    payment_mode: PaymentMode | None = None


class PaymentCreate(BaseModel):
    reference_type: PaymentReferenceType
    reference_id: PydanticObjectId

    direction: PaymentDirection

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    payment_mode: PaymentMode
    payment_date: datetime

    notes: str | None = None


class PaymentResponse(BaseModel):
    id: PydanticObjectId

    reference_type: PaymentReferenceType | None = None
    reference_id: PydanticObjectId | None = None

    direction: PaymentDirection | None = None

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    payment_mode: PaymentMode
    payment_date: datetime

    notes: str | None = None

    @classmethod
    def from_document(cls, payment: Payment | MechanicInvoicePayment):
        if hasattr(payment, "invoice"):
            return cls(
                id=payment.id,
                amount=payment.amount,
                payment_mode=payment.payment_mode,
                payment_date=payment.payment_date,
                notes=payment.notes,
            )
        else:
            return cls(
                id=payment.id,
                reference_type=payment.reference_type,
                reference_id=payment.reference_id,
                direction=payment.direction,
                amount=payment.amount,
                payment_mode=payment.payment_mode,
                payment_date=payment.payment_date,
                notes=payment.notes,
            )
