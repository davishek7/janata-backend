from enum import Enum


class SaleType(str, Enum):
    SALE = "SALE"
    QUICK_SALE = "QUICK_SALE"
    SCRAP_SALE = "SCRAP_SALE"
