from .base import BaseDocument
from pydantic import Field
from decimal import Decimal
from datetime import date
from .scrap_purchase_item import ScrapPurchaseItem
from app.enums.PaymentStatus import PaymentStatus


class ScrapPurchase(BaseDocument):
    purchase_number: str | None = None

    transaction_date: date

    seller_name: str | None = None

    seller_phone: str | None = None

    seller_address: str | None = None

    scrap_items: list[ScrapPurchaseItem]

    total_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    paid_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    payment_status: PaymentStatus

    @property
    def due_amount(self) -> Decimal:
        return self.total_amount - self.paid_amount

    class Settings:
        name = "scrap_purchases"
