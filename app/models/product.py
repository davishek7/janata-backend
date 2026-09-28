from beanie import Link
from pydantic import Field
from decimal import Decimal
from .base import BaseDocument
from app.enums.ProductCategory import ProductCategory
from .vendor import Vendor


class Product(BaseDocument):
    name: str

    category: ProductCategory

    serialized: bool = False

    foc_months: int = 0

    prorata_months: int = 0

    stock_quantity: int = 0

    purchase_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    default_selling_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    default_vendor: Link[Vendor] | None = None

    low_stock_threshold: int = 0

    class Settings:
        name = "products"
