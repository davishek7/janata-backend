from datetime import date
from beanie import Link
from pydantic import Field
from decimal import Decimal
from .base import BaseDocument
from .user import User
from .mechanic import Mechanic
from .quick_sale_item import QuickSaleItem
from app.enums.PaymentStatus import PaymentStatus
from app.enums.LabourType import LabourType


class QuickSale(BaseDocument):
    sale_number: str
    sale_date: date

    items: list[QuickSaleItem]

    items_total: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    discount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    total_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    paid_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    labour_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    labour_type: LabourType | None = None
    staff: Link[User] | None = None
    mechanic: Link[Mechanic] | None = None

    payment_status: PaymentStatus

    remarks: str | None = None

    @property
    def due_amount(self) -> Decimal:
        return self.total_amount - self.paid_amount

    class Settings:
        name = "quick_sales"
