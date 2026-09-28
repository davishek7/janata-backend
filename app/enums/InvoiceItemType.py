from enum import Enum


class InvoiceItemType(str, Enum):
    PRODUCT = "PRODUCT"
    LABOUR = "LABOUR"
    SERVICE = "SERVICE"
