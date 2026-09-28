from enum import Enum


class InvoiceType(str, Enum):
    BATTERY_SALE = "BATTERY_SALE"
    MECHANIC_JOB = "MECHANIC_JOB"
