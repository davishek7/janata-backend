from .base import BaseDocument
from beanie import PydanticObjectId
from pydantic import Field
from decimal import Decimal
from datetime import datetime
from app.enums.PaymentMode import PaymentMode
from app.enums.PaymentDirection import PaymentDirection
from app.enums.PaymentReferenceType import PaymentReferenceType


class Payment(BaseDocument):
    reference_type: PaymentReferenceType
    reference_id: PydanticObjectId

    direction: PaymentDirection

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    payment_mode: PaymentMode
    payment_date: datetime

    notes: str | None = None

    class Settings:
        name = "payments"
