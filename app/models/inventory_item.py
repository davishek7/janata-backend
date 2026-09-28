from beanie import Link
from pydantic import Field
from datetime import date
from decimal import Decimal
from .base import BaseDocument
from app.enums.InventoryStatus import InventoryStatus
from app.models.product import Product


class InventoryItem(BaseDocument):
    product: Link[Product]

    serial_number: str

    purchase_date: date | None = None

    purchase_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    status: InventoryStatus = InventoryStatus.IN_STOCK

    class Settings:
        name = "inventory_items"
