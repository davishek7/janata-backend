from pydantic import BaseModel, Field
from beanie import PydanticObjectId
from decimal import Decimal
from datetime import date, datetime
from app.enums.PaymentMode import PaymentMode
from app.enums.PaymentStatus import PaymentStatus
from app.enums.QuickSaleItemType import QuickSaleItemType


class ScrapSaleItemCreate(BaseModel):
    item_type: QuickSaleItemType

    product_id: PydanticObjectId | None = None

    description: str | None = None

    quantity: int = 0

    weight: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    selling_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class ScrapSaleCreate(BaseModel):
    transaction_date: date

    buyer_name: str | None

    items: list[ScrapSaleItemCreate]

    paid_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)
    payment_date: datetime | None = None
    payment_mode: PaymentMode | None = None
