from .base import BaseDocument
from beanie import PydanticObjectId
from datetime import date
from decimal import Decimal
from pydantic import Field
from app.enums.LedgerType import LedgerType
from app.enums.PaymentMode import PaymentMode
from app.enums.LedgerEntryType import LedgerEntryType


class LedgerEntry(BaseDocument):
    transaction_date: date

    entry_type: LedgerEntryType

    ledger_type: LedgerType

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    payment_mode: PaymentMode

    balance: Decimal = Field(default=0, max_digits=12, decimal_places=2)

    remarks: str | None = None

    reference_id: PydanticObjectId | None = None

    class Settings:
        name = "ledger_entries"
