from pydantic import BaseModel, Field
from decimal import Decimal
from beanie import PydanticObjectId
from datetime import date
from app.enums.StaffLedgerType import StaffLedgerType
from app.models import StaffLedger


class StaffLedgerCreate(BaseModel):
    transaction_date: date

    transaction_type: StaffLedgerType

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    description: str | None = None

    reference_id: PydanticObjectId | None = None


class StaffLedgerResponse(BaseModel):
    id: PydanticObjectId

    staff_name: str

    transaction_date: date

    transaction_type: StaffLedgerType

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    balance: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    description: str | None = None

    reference_id: PydanticObjectId | None = None

    @classmethod
    def from_document(cls, ledger: StaffLedger):
        return cls(
            id=ledger.id,
            staff_name=ledger.staff.name,
            transaction_date=ledger.transaction_date,
            transaction_type=ledger.transaction_type,
            amount=ledger.amount,
            balance=ledger.balance,
            description=ledger.description,
            reference_id=ledger.reference_id,
        )
