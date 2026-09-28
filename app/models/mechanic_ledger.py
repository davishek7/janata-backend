from beanie import Link, PydanticObjectId
from datetime import date
from pydantic import Field
from decimal import Decimal
from .base import BaseDocument
from .mechanic import Mechanic
from app.enums.MechanicLedgerType import MechanicLedgerType
from app.enums.PaymentMode import PaymentMode


class MechanicLedger(BaseDocument):
    transaction_date: date

    mechanic: Link[Mechanic]

    transaction_type: MechanicLedgerType

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    balance: Decimal = Field(default=0, max_digits=12, decimal_places=2)

    payment_mode: PaymentMode | None = None

    description: str | None = None

    reference_id: PydanticObjectId | None = None

    class Settings:
        name = "mechanic_ledgers"
