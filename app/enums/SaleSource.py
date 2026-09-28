from enum import Enum


class SaleSource(str, Enum):
    SYSTEM = "SYSTEM"
    LEGACY = "LEGACY"
