from enum import Enum


class PaymentMode(str, Enum):
    CASH = "CASH"
    UPI = "UPI"
    BANK = "BANK"
