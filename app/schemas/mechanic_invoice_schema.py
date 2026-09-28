from pydantic import BaseModel, Field
from beanie import PydanticObjectId
from decimal import Decimal
from datetime import datetime, date
from app.enums.PaymentMode import PaymentMode
from app.models.mechanic_invoice_payment import MechanicInvoicePayment
from app.models import InvoiceItem


class MechanicInvoiceCreate(BaseModel):
    invoice_date: date
    customer_name: str
    customer_address: str
    customer_phone: str | None = None
    vehicle_number: str | None = None
    items: list[InvoiceItem]
    discount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)
    advance_paid: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)
    advance_date: datetime | None = None
    advance_payment_mode: PaymentMode | None = None


class MechanicInvoicePaymentCreate(BaseModel):
    invoice_id: PydanticObjectId
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    payment_mode: PaymentMode
    payment_date: datetime
    notes: str | None = None


class MechanicInvoicePaymentResponse(BaseModel):
    id: PydanticObjectId
    payment_date: datetime
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    payment_mode: PaymentMode
    notes: str | None = None

    @classmethod
    def from_document(cls, payment: MechanicInvoicePayment):
        return cls(
            id=payment.id,
            payment_date=payment.payment_date,
            amount=payment.amount,
            payment_mode=payment.payment_mode,
            notes=payment.notes,
        )
