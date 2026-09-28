from enum import Enum


class PaymentDirection(str, Enum):
    RECEIVED = "RECEIVED"
    PAID = "PAID"
