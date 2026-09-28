from pydantic import Field
from decimal import Decimal
from beanie import Link
from .product import Product
from .base import AppBaseModel
from app.enums.QuickSaleItemType import QuickSaleItemType


class QuickSaleItem(AppBaseModel):
    item_type: QuickSaleItemType

    product: Link[Product] | None = None

    description: str | None = None

    quantity: int

    selling_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    @property
    def total_amount(self) -> Decimal:
        return self.quantity * self.selling_price
