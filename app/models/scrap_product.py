from .base import BaseDocument
from pydantic import Field
from decimal import Decimal


class ScrapProduct(BaseDocument):
    name: str

    description: str | None = None

    stock_quantity: int = 0

    purchase_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    selling_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    class Settings:
        name = "scrap_products"
