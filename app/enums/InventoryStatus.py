from enum import Enum


class InventoryStatus(str, Enum):
    IN_STOCK = "IN_STOCK"
    SOLD = "SOLD"
    CLAIMED = "CLAIMED"
    SCRAPED = "SCRAPED"
