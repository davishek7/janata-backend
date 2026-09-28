from beanie import Link
from datetime import date
from .base import BaseDocument
from .warranty import Warranty
from app.enums.WarrantyClaimStatus import WarrantyClaimStatus
from .inventory_item import InventoryItem


class WarrantyClaim(BaseDocument):
    claim_number: str

    warranty: Link[Warranty]

    battery_received_date: date | None = None

    sent_to_dealer_date: date | None = None

    returned_date: date | None = None

    decision_date: date | None = None

    status: WarrantyClaimStatus

    replacement_serial_number: str | None = None

    replacement_inventory_item: Link[InventoryItem] | None = None

    remarks: str | None = None

    class Settings:
        name = "warranty_claims"
