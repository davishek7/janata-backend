from beanie import Link
from datetime import date
from pydantic import Field
from decimal import Decimal
from .base import BaseDocument
from .sale_item import SaleItem
from .invoice import Invoice
from .scrap_receive import ScrapReceive
from app.enums.SaleSource import SaleSource


class Sale(BaseDocument):
    sale_number: str | None = None

    source: SaleSource

    customer_name: str

    customer_address: str

    customer_phone: str | None = None

    vehicle_number: str | None = None

    items: list[SaleItem]

    scrap_received: list[ScrapReceive] = []

    sale_date: date

    items_total: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    discount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    scrap_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    total_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    invoice: Link[Invoice] | None = None

    class Settings:
        name = "sales"
