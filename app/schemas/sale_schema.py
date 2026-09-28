from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date
from typing import List
from beanie import PydanticObjectId
from app.enums.SaleSource import SaleSource
from app.enums.PaymentMode import PaymentMode
from app.enums.PaymentStatus import PaymentStatus
from app.models import Sale, ScrapReceive, SaleItem
from .common.query_params import PaginationQueryParams, SearchQueryParams


class SaleQueryParams(PaginationQueryParams, SearchQueryParams):
    source: SaleSource | None = None
    payment_status: PaymentStatus | None = None


class ScrapReceiveCreate(BaseModel):
    scrap_product_id: PydanticObjectId

    quantity: int

    exchange_value: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class SaleItemCreate(BaseModel):
    product_id: PydanticObjectId

    serial_number: str

    selling_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class SaleCreate(BaseModel):
    source: SaleSource

    customer_name: str

    customer_address: str

    customer_phone: str | None = None

    vehicle_number: str | None = None

    items: List[SaleItemCreate]

    scrap_received: List[ScrapReceiveCreate] | None = None

    discount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    sale_date: date

    initial_payment: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    payment_mode: PaymentMode | None = None


class SaleItemResponse(BaseModel):
    product_name: str

    serial_number: str

    selling_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    @classmethod
    def from_document(cls, item: SaleItem):
        return cls(
            product_name=item.product.name,
            serial_number=item.serial_number,
            selling_price=item.selling_price,
        )


class ScrapReceivedResponse(BaseModel):
    scrap_product_name: str

    quantity: int

    exchange_value: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    @classmethod
    def from_document(cls, scrap_item: ScrapReceive):
        return cls(
            scrap_product_name=scrap_item.product.name,
            quantity=scrap_item.quantity,
            exchange_value=scrap_item.exchange_value,
        )


class SaleListResponse(BaseModel):
    id: PydanticObjectId

    sale_number: str | None = None

    source: SaleSource

    customer_name: str

    sale_date: date

    payment_status: PaymentStatus

    @classmethod
    def from_document(cls, sale: Sale):
        return cls(
            id=sale.id,
            sale_number=sale.sale_number,
            source=sale.source,
            customer_name=sale.customer_name,
            sale_date=sale.sale_date,
            payment_status=sale.invoice.payment_status,
        )


class SaleDetailsResponse(SaleListResponse):
    customer_address: str

    customer_phone: str | None = None

    vehicle_number: str | None = None

    items: List[SaleItemResponse]

    scrap_received: List[ScrapReceivedResponse] | None = None

    items_total: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    discount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    scrap_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    total_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    invoice_id: PydanticObjectId

    @classmethod
    def from_document(cls, sale: Sale):
        return cls(
            id=sale.id,
            sale_number=sale.sale_number,
            source=sale.source,
            customer_name=sale.customer_name,
            customer_address=sale.customer_address,
            customer_phone=sale.customer_phone,
            vehicle_number=sale.vehicle_number,
            items=[SaleItemResponse.from_document(item) for item in sale.items],
            scrap_received=[
                ScrapReceivedResponse.from_document(scrap_item)
                for scrap_item in sale.scrap_received
            ],
            items_total=sale.items_total,
            discount=sale.discount,
            scrap_amount=sale.scrap_amount,
            total_amount=sale.total_amount,
            sale_date=sale.sale_date,
            payment_status=sale.invoice.payment_status,
            invoice_id=sale.invoice.id,
        )
