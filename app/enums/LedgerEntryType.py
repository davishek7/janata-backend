from enum import Enum


class LedgerEntryType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
