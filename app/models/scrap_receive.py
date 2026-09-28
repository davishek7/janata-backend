from pydantic import BaseModel, Field
from decimal import Decimal
from beanie import Link
from .scrap_product import ScrapProduct


class ScrapReceive(BaseModel):
    product: Link[ScrapProduct]

    quantity: int = 1

    exchange_value: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
