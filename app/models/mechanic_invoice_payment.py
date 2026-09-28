from .base import BaseDocument
from beanie import Link
from pydantic import Field
from datetime import datetime
from decimal import Decimal
from .invoice import Invoice
from app.enums.PaymentMode import PaymentMode


class MechanicInvoicePayment(BaseDocument):
    invoice: Link[Invoice]

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    payment_mode: PaymentMode
    payment_date: datetime

    notes: str | None = None

    class Settings:
        name = "mechanic_invoice_payments"
