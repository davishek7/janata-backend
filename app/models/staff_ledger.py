from beanie import Link, PydanticObjectId
from pydantic import Field
from decimal import Decimal
from datetime import date
from .base import BaseDocument
from .user import User
from app.enums.StaffLedgerType import StaffLedgerType


class StaffLedger(BaseDocument):
    transaction_date: date

    staff: Link[User]

    transaction_type: StaffLedgerType

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    balance: Decimal = Field(default=0, max_digits=12, decimal_places=2)

    description: str | None = None

    reference_id: PydanticObjectId | None = None

    class Settings:
        name = "staff_ledgers"
