from pydantic import Field
from decimal import Decimal
from datetime import date
from .base import BaseDocument
from .scrap_sale_item import ScrapSaleItem
from app.enums.PaymentStatus import PaymentStatus


class ScrapSale(BaseDocument):
    sale_number: str

    transaction_date: date

    buyer_name: str | None = None

    items: list[ScrapSaleItem]

    total_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    paid_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    payment_status: PaymentStatus

    @property
    def due_amount(self) -> Decimal:
        return self.total_amount - self.paid_amount

    class Settings:
        name = "scrap_sales"
