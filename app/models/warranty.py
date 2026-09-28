from beanie import Link, Indexed
from datetime import date
from .base import BaseDocument
from .sale import Sale
from .product import Product


class Warranty(BaseDocument):
    sale: Link[Sale]

    product: Link[Product]

    foc_end_date: date

    prorata_end_date: date

    original_serial_number: Indexed(str, unique=True) | None = None  # type: ignore

    current_serial_number: Indexed(str, unique=True)  # type: ignore

    is_consumed: bool = False

    class Settings:
        name = "warranties"
