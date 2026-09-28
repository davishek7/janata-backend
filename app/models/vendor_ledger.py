from beanie import Link
from datetime import date
from pydantic import Field
from decimal import Decimal
from .base import BaseDocument
from app.enums.VendorLedgerType import VendorLedgerType
from app.models.vendor import Vendor


class VendorLedger(BaseDocument):
    vendor: Link[Vendor]

    transaction_date: date

    ledger_type: VendorLedgerType

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    balance: Decimal = Field(deafult=0, max_digits=12, decimal_places=2)

    remarks: str | None = None

    class Settings:
        name = "vendor_ledgers"
