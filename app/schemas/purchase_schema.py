from beanie import PydanticObjectId
from datetime import date
from pydantic import BaseModel, Field
from decimal import Decimal
from app.models import Purchase, PurchaseItem
from .common.query_params import PaginationQueryParams, SearchQueryParams


class PurchaseQueryParams(PaginationQueryParams, SearchQueryParams):
    pass


class PurchaseItemCreate(BaseModel):
    product_id: PydanticObjectId

    quantity: int = Field(gt=0)

    discount_percentage: int = 0

    purchase_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    # Required only for serialized products
    serial_numbers: list[str] = Field(default_factory=list)


class PurchaseCreate(BaseModel):
    purchase_date: date = Field(default_factory=date.today)

    invoice_number: str | None = None

    items: list[PurchaseItemCreate]


class PurchaseItemResponse(BaseModel):
    product_id: PydanticObjectId

    product_name: str

    quantity: int

    discount_percentage: int = 0

    purchase_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    item_total_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    @classmethod
    def from_document(cls, item: PurchaseItem):
        return cls(
            product_id=item.product.id,
            product_name=item.product.name,
            quantity=item.quantity,
            discount_percentage=item.discount_percentage,
            purchase_price=item.purchase_price,
            item_total_amount=item.item_total_amount,
        )


class PurchaseListResponse(BaseModel):
    id: PydanticObjectId

    purchase_number: str | None = None

    purchase_date: date

    invoice_number: str | None

    total_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    @classmethod
    def from_document(cls, purchase: Purchase):
        return cls(
            id=purchase.id,
            purchase_number=purchase.purchase_number,
            purchase_date=purchase.purchase_date,
            invoice_number=purchase.invoice_number,
            total_amount=purchase.total_amount,
        )


class PurchaseDetailsResponse(PurchaseListResponse):
    items: list[PurchaseItemResponse]

    @classmethod
    def from_document(cls, purchase: Purchase):
        return cls(
            id=purchase.id,
            purchase_number=purchase.purchase_number,
            purchase_date=purchase.purchase_date,
            invoice_number=purchase.invoice_number,
            items=[PurchaseItemResponse.from_document(item) for item in purchase.items],
            total_amount=purchase.total_amount,
        )
