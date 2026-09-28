from beanie import Link
from datetime import date
from pydantic import Field
from decimal import Decimal
from .base import BaseDocument
from .vendor import Vendor
from .purchase_item import PurchaseItem


class Purchase(BaseDocument):
    purchase_number: str | None = None

    vendor: Link[Vendor]

    purchase_date: date

    invoice_number: str | None = None

    items: list[PurchaseItem]

    total_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    class Settings:
        name = "purchases"
