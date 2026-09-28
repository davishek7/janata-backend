from pydantic import BaseModel, Field
from beanie import PydanticObjectId
from decimal import Decimal
from datetime import date, datetime
from app.models import QuickSale, QuickSaleItem, Payment
from app.enums.PaymentStatus import PaymentStatus
from app.enums.PaymentMode import PaymentMode
from app.enums.LabourType import LabourType
from app.enums.QuickSaleItemType import QuickSaleItemType
from app.schemas.payment_schema import PaymentResponse
from .common.query_params import PaginationQueryParams, SearchQueryParams


class QuickSaleQueryParams(PaginationQueryParams, SearchQueryParams):
    payment_status: PaymentStatus | None = None


class QuickSaleItemCreate(BaseModel):
    item_type: QuickSaleItemType

    product_id: PydanticObjectId | None = None

    description: str | None = None

    quantity: int

    selling_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class QuickSaleCreate(BaseModel):
    sale_date: date

    items: list[QuickSaleItemCreate]

    discount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)
    labour_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    labour_type: LabourType | None = None
    staff_id: PydanticObjectId | None = None
    mechanic_id: PydanticObjectId | None = None

    remarks: str | None = None

    paid_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)
    payment_date: datetime | None = None
    payment_mode: PaymentMode | None = None


class QuickSaleItemResponse(BaseModel):
    item_type: QuickSaleItemType
    product_name: str | None = None
    description: str | None = None
    quantity: int
    selling_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    total_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    @classmethod
    def from_document(cls, item: QuickSaleItem):
        return cls(
            item_type=item.item_type,
            product_name=item.product.name if item.product else None,
            description=item.description if item.description else None,
            quantity=item.quantity,
            selling_price=item.selling_price,
            total_amount=item.total_amount,
        )


class QuickSaleList(BaseModel):
    id: PydanticObjectId
    sale_number: str
    sale_date: date
    payment_status: PaymentStatus
    remarks: str | None = None

    @classmethod
    def from_document(cls, sale: QuickSale):
        return cls(
            id=sale.id,
            sale_number=sale.sale_number,
            sale_date=sale.sale_date,
            payment_status=sale.payment_status,
            remarks=sale.remarks,
        )


class QuickSaleDetails(QuickSaleList):
    items: list[QuickSaleItemResponse]
    items_total: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    discount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)
    total_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    paid_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)
    labour_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)
    labour_type: LabourType | None = None
    staff_name: str | None = None
    mechanic_name: str | None = None
    payments: list[PaymentResponse]

    @classmethod
    def from_document(cls, sale: QuickSale, payments: list[Payment]):
        return cls(
            id=sale.id,
            sale_number=sale.sale_number,
            sale_date=sale.sale_date,
            items=[QuickSaleItemResponse.from_document(item) for item in sale.items],
            items_total=sale.items_total,
            discount=sale.discount,
            total_amount=sale.total_amount,
            paid_amount=sale.paid_amount,
            labour_amount=sale.labour_amount,
            labour_type=sale.labour_type,
            staff_name=sale.staff.full_name if sale.staff else None,
            mechanic_name=sale.mechanic.full_name if sale.mechanic else None,
            payments=[PaymentResponse.from_document(payment) for payment in payments],
            payment_status=sale.payment_status,
            remarks=sale.remarks,
        )
