from pydantic import Field
from decimal import Decimal
from beanie import Link
from .scrap_product import ScrapProduct
from .base import AppBaseModel
from app.enums.QuickSaleItemType import QuickSaleItemType


class ScrapSaleItem(AppBaseModel):
    item_type: QuickSaleItemType

    product: Link[ScrapProduct] | None = None

    description: str | None = None

    quantity: int | None = None

    weight: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    selling_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    @property
    def total_amount(self) -> Decimal:
        if self.quantity:
            return self.quantity * self.selling_price
        if self.weight:
            return self.weight * self.selling_price
