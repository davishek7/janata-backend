from pydantic import BaseModel, Field
from decimal import Decimal
from beanie import Link
from uuid import uuid4, UUID
from .inventory_item import InventoryItem
from .product import Product
from .base import AppBaseModel


class SaleItem(AppBaseModel):
    id: UUID = Field(default_factory=uuid4)

    product: Link[Product]

    inventory_item: Link[InventoryItem] | None = None

    serial_number: str

    selling_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
