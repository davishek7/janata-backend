from enum import Enum


class WarrantyStatus(str, Enum):
    FOC = "FOC"
    PRORATA = "PRORATA"
    EXPIRED = "EXPIRED"
