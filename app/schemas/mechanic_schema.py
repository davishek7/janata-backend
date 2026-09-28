from pydantic import BaseModel, Field
from decimal import Decimal
from beanie import PydanticObjectId
from datetime import date
from app.models import Mechanic, MechanicLedger
from app.enums.PaymentMode import PaymentMode
from app.enums.MechanicLedgerType import MechanicLedgerType
from .common.query_params import PaginationQueryParams, SearchQueryParams


class MechanicQueryParams(PaginationQueryParams, SearchQueryParams):
    pass


class MechanicCreate(BaseModel):
    full_name: str

    phone: str | None = None


class MechanicResponse(BaseModel):
    id: PydanticObjectId

    full_name: str

    phone: str | None = None

    @classmethod
    def from_document(cls, mechanic: Mechanic):
        return cls(id=mechanic.id, full_name=mechanic.full_name, phone=mechanic.phone)


class ProductTakenCreate(BaseModel):
    product_id: PydanticObjectId

    quantity: int

    selling_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    transaction_date: date

    description: str | None = None

    sale_id: PydanticObjectId | None = None


class MechanicLedgerCreate(BaseModel):
    transaction_date: date

    transaction_type: MechanicLedgerType

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    payment_mode: PaymentMode | None = None

    description: str | None = None

    reference_id: PydanticObjectId | None = None


class MechanicLedgerResponse(BaseModel):
    id: PydanticObjectId

    transaction_date: date

    mechanic_name: str

    transaction_type: MechanicLedgerType

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    payment_mode: PaymentMode | None = None

    balance: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    description: str | None = None

    reference_id: PydanticObjectId | None = None

    @classmethod
    def from_document(cls, mechanic_ledger: MechanicLedger):
        return cls(
            id=mechanic_ledger.id,
            transaction_date=mechanic_ledger.transaction_date,
            mechanic_name=mechanic_ledger.mechanic.full_name,
            transaction_type=mechanic_ledger.transaction_type,
            amount=mechanic_ledger.amount,
            payment_mode=mechanic_ledger.payment_mode,
            balance=mechanic_ledger.balance,
            description=mechanic_ledger.description,
            reference_id=mechanic_ledger.reference_id,
        )


class MechanicLookupResponse(BaseModel):
    id: PydanticObjectId

    full_name: str

    @classmethod
    def from_document(cls, mechanic: Mechanic):
        return cls(id=mechanic.id, full_name=mechanic.full_name)
