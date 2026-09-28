from .base import BaseDocument


class Vendor(BaseDocument):
    vendor_name: str

    address: str

    phone: str

    contact_person: str | None = None

    contact_person_phone: str | None = None

    class Settings:
        name = "vendors"
