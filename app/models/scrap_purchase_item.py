from pydantic import Field
from decimal import Decimal
from beanie import Link
from .scrap_product import ScrapProduct
from .base import AppBaseModel


class ScrapPurchaseItem(AppBaseModel):
    product: Link[ScrapProduct]

    quantity: int

    purchase_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    @property
    def total_amount(self) -> Decimal:
        return self.quantity * self.purchase_price
