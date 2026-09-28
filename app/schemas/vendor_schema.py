from pydantic import BaseModel, Field
from decimal import Decimal
from beanie import PydanticObjectId
from datetime import date
from app.models import Vendor, VendorLedger
from app.enums.VendorLedgerType import VendorLedgerType
from app.enums.PaymentMode import PaymentMode
from .common.query_params import PaginationQueryParams, SearchQueryParams


class VendorQueryParams(PaginationQueryParams, SearchQueryParams):
    pass


class VendorCreate(BaseModel):
    vendor_name: str

    address: str

    phone: str

    contact_person: str | None = None

    contact_person_phone: str | None = None


class VendorUpdate(BaseModel):
    vendor_name: str | None = None

    address: str | None = None

    phone: str | None = None

    contact_person: str | None = None

    contact_person_phone: str | None = None


class VendorResponse(BaseModel):
    id: PydanticObjectId

    vendor_name: str

    address: str

    phone: str

    contact_person: str | None = None

    contact_person_phone: str | None = None

    @classmethod
    def from_document(cls, vendor: Vendor):
        return cls(
            id=vendor.id,
            vendor_name=vendor.vendor_name,
            address=vendor.address,
            phone=vendor.phone,
            contact_person=vendor.contact_person,
            contact_person_phone=vendor.contact_person_phone,
        )


class VendorLookupResponse(BaseModel):
    id: PydanticObjectId
    vendor_name: str

    @classmethod
    def from_document(cls, vendor: Vendor):
        return cls(id=vendor.id, vendor_name=vendor.vendor_name)


class VendorPaymentCreate(BaseModel):
    vendor_id: PydanticObjectId

    transaction_date: date

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    payment_mode: PaymentMode

    remarks: str | None = None


class VendorLedgerResponse(BaseModel):
    id: PydanticObjectId

    transaction_date: date

    ledger_type: VendorLedgerType

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    balance: Decimal = Field(deafult=0, max_digits=12, decimal_places=2)

    remarks: str | None = None

    @classmethod
    def from_document(cls, ledger: VendorLedger):
        return cls(
            id=ledger.id,
            transaction_date=ledger.transaction_date,
            ledger_type=ledger.ledger_type,
            amount=ledger.amount,
            balance=ledger.balance,
            remarks=ledger.remarks,
        )


class VendorLedgerQueryParams(PaginationQueryParams, SearchQueryParams):
    ledger_type: VendorLedgerType | None = None
