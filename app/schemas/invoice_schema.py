from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date
from beanie import PydanticObjectId, Link
from app.enums.InvoiceType import InvoiceType
from app.enums.PaymentStatus import PaymentStatus
from app.enums.InvoiceItemType import InvoiceItemType
from app.models import Invoice, InvoiceItem, Mechanic, Payment, MechanicInvoicePayment
from app.enums.InvoiceType import InvoiceType
from .common.query_params import PaginationQueryParams, SearchQueryParams
from .payment_schema import PaymentResponse


class InvoiceQueryParams(
    PaginationQueryParams,
    SearchQueryParams,
):
    payment_status: PaymentStatus | None = None
    invoice_type: InvoiceType | None = None


class InvoiceCreate(BaseModel):
    invoice_number: str

    invoice_date: date

    invoice_type: InvoiceType

    customer_name: str

    customer_address: str

    customer_phone: str | None = None

    vehicle_number: str | None = None

    mechanic: Link[Mechanic] | None = None

    items: list[InvoiceItem]

    items_total: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    discount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    scrap_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    total_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    paid_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    payment_status: PaymentStatus


class InvoiceItemResponse(BaseModel):
    item_type: InvoiceItemType

    product_name: str | None = None

    quantity: int

    unit_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    serial_number: str | None = None

    description: str

    total_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    @classmethod
    def from_document(cls, item: InvoiceItem):
        return cls(
            item_type=item.item_type,
            product_name=item.product.name if item.product else None,
            quantity=item.quantity,
            unit_price=item.unit_price,
            serial_number=item.serial_number,
            description=item.description,
            total_amount=item.total_amount,
        )


class InvoiceListResponse(BaseModel):
    id: PydanticObjectId

    invoice_date: date

    invoice_number: str

    invoice_type: InvoiceType

    customer_name: str

    mechanic_name: str | None = None

    payment_status: PaymentStatus

    @classmethod
    def from_document(cls, invoice: Invoice):
        return cls(
            id=invoice.id,
            invoice_date=invoice.invoice_date,
            invoice_number=invoice.invoice_number,
            invoice_type=invoice.invoice_type,
            customer_name=invoice.customer_name,
            mechanic_name=invoice.mechanic.full_name if invoice.mechanic else None,
            payment_status=invoice.payment_status,
        )


class InvoiceDetailsResponse(InvoiceListResponse):
    customer_address: str

    customer_phone: str | None = None

    vehicle_number: str | None = None

    items: list[InvoiceItemResponse]

    items_total: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    discount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    scrap_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    total_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    paid_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    due_amount: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    payments: list[PaymentResponse]

    @classmethod
    def from_document(
        cls, invoice: Invoice, payments: list[Payment] | list[MechanicInvoicePayment]
    ):
        return cls(
            id=invoice.id,
            invoice_date=invoice.invoice_date,
            invoice_number=invoice.invoice_number,
            invoice_type=invoice.invoice_type,
            customer_name=invoice.customer_name,
            customer_address=invoice.customer_address,
            customer_phone=invoice.customer_phone,
            vehicle_number=invoice.vehicle_number,
            mechanic_name=invoice.mechanic.full_name if invoice.mechanic else None,
            items=[InvoiceItemResponse.from_document(item) for item in invoice.items],
            items_total=invoice.items_total,
            discount=invoice.discount,
            scrap_amount=invoice.scrap_amount,
            total_amount=invoice.total_amount,
            paid_amount=invoice.paid_amount,
            due_amount=invoice.due_amount,
            payments=[PaymentResponse.from_document(payment) for payment in payments],
            payment_status=invoice.payment_status,
        )
