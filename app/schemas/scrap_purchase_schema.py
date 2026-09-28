from pydantic import BaseModel, Field
from beanie import PydanticObjectId
from decimal import Decimal
from datetime import date
from app.enums.PaymentMode import PaymentMode
from app.enums.PaymentStatus import PaymentStatus
from app.models import ScrapPurchase, ScrapPurchaseItem
from .common.query_params import PaginationQueryParams, SearchQueryParams


class ScrapPurchaseQueryParams(PaginationQueryParams, SearchQueryParams):
    payment_status: PaymentStatus | None = None
    payment_mode: PaymentMode | None = None


class ScrapPurchaseItem(BaseModel):
    product_id: PydanticObjectId

    quantity: int

    purchase_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class ScrapPurchaseItemResponse(BaseModel):
    product_id: PydanticObjectId

    product_name: str

    quantity: int

    purchase_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    @classmethod
    def from_document(cls, item: ScrapPurchaseItem):
        return cls(
            product_id=item.product.id,
            product_name=item.product.name,
            quantity=item.quantity,
            purchase_price=item.purchase_price,
        )


class ScrapPurchaseCreate(BaseModel):
    transaction_date: date

    seller_name: str | None = None

    seller_phone: str | None = None

    seller_address: str | None = None

    scrap_items: list[ScrapPurchaseItem]

    paid_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    payment_status: PaymentStatus


class ScrapPurchaseListResponse(BaseModel):
    id: PydanticObjectId

    purchase_number: str

    transaction_date: date

    seller_name: str | None = None

    total_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    payment_status: PaymentStatus

    @classmethod
    def from_document(cls, purchase: ScrapPurchase):
        return cls(
            id=purchase.id,
            purchase_number=purchase.purchase_number,
            transaction_date=purchase.transaction_date,
            seller_name=purchase.seller_name,
            total_amount=purchase.total_amount,
            payment_status=purchase.payment_status,
        )


class ScrapPurchaseDetailsResponse(BaseModel):
    seller_phone: str | None = None

    seller_address: str | None = None

    scrap_items: list[ScrapPurchaseItemResponse]

    paid_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    due_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    payment_mode: PaymentMode

    @classmethod
    def from_document(cls, purchase: ScrapPurchase):
        return cls(
            id=purchase.id,
            purchase_number=purchase.purchase_number,
            transaction_date=purchase.transaction_date,
            seller_name=purchase.seller_name,
            seller_phone=purchase.seller_phone,
            seller_address=purchase.seller_address,
            scrap_items=[
                ScrapPurchaseItemResponse.from_document(item)
                for item in purchase.scrap_items
            ],
            total_amount=purchase.total_amount,
            paid_amount=purchase.paid_amount,
            due_amount=purchase.due_amount,
            payment_status=purchase.payment_status,
            payment_mode=purchase.payment_mode,
        )
