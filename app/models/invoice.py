from beanie import Link
from datetime import date
from pydantic import Field
from decimal import Decimal
from .base import BaseDocument
from app.enums.InvoiceType import InvoiceType
from .mechanic import Mechanic
from .invoice_item import InvoiceItem
from app.enums.PaymentStatus import PaymentStatus


class Invoice(BaseDocument):
    invoice_number: str

    invoice_date: date | None = None

    invoice_type: InvoiceType

    customer_name: str

    customer_address: str

    customer_phone: str | None = None

    vehicle_number: str | None = None

    mechanic: Link[Mechanic] | None = None

    items: list[InvoiceItem]

    items_total: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    discount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    scrap_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    total_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    paid_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    payment_status: PaymentStatus

    @property
    def due_amount(self) -> Decimal:
        return self.total_amount - self.paid_amount

    class Settings:
        name = "invoices"
