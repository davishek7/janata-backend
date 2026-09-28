from beanie import Link
from pydantic import Field
from decimal import Decimal
from app.enums.InvoiceItemType import InvoiceItemType
from app.models.product import Product
from .base import AppBaseModel


class InvoiceItem(AppBaseModel):
    item_type: InvoiceItemType

    description: str

    quantity: int = 1

    unit_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    product: Link[Product] | None = None

    serial_number: str | None = None

    @property
    def total_amount(self) -> Decimal:
        return self.quantity * self.unit_price
