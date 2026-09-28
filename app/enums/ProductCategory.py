from enum import Enum


class ProductCategory(str, Enum):
    BATTERY = "BATTERY"
    INVERTER = "INVERTER"
    ENGINE_OIL = "ENGINE_OIL"
    DISTILLED_WATER = "DISTILLED_WATER"
    ACCESSORY = "ACCESSORY"
