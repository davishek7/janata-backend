from enum import Enum


class VendorLedgerType(str, Enum):
    OPENING_BALANCE = "OPENING_BALANCE"

    PURCHASE = "PURCHASE"

    PAYMENT = "PAYMENT"
