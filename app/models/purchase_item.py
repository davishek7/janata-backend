from beanie import Link
from pydantic import Field
from decimal import Decimal
from .product import Product
from .base import AppBaseModel


class PurchaseItem(AppBaseModel):
    product: Link[Product]

    quantity: int

    discount_percentage: int = 0

    purchase_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    @property
    def item_total_amount(self) -> Decimal:
        return self.quantity * (
            self.purchase_price - (self.purchase_price * self.discount_percentage / 100)
        )
