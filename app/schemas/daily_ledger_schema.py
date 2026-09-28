from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date
from beanie import PydanticObjectId
from app.enums.LedgerEntryType import LedgerEntryType
from app.enums.LedgerType import LedgerType
from app.enums.PaymentMode import PaymentMode


class LedgerCreate(BaseModel):
    transaction_date: date

    entry_type: LedgerEntryType

    ledger_type: LedgerType

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    payment_mode: PaymentMode

    description: str | None = None

    reference_id: PydanticObjectId | None = None
