from fastapi import status, Depends
import re
from beanie import PydanticObjectId
from beanie.operators import Or
from pymongo.asynchronous.client_session import AsyncClientSession
from app.exceptions.custom_exception import AppException
from app.models import Invoice, Payment, MechanicInvoicePayment
from app.enums.PaymentReferenceType import PaymentReferenceType
from app.services.daily_ledger_service import DailyLegerService
from app.schemas.invoice_schema import (
    InvoiceCreate,
    InvoiceListResponse,
    InvoiceDetailsResponse,
    InvoiceQueryParams,
)
from app.utils.pagination import paginate
from app.schemas.common.pagination_schema import PaginatedResponse, Pagination


class InvoiceService:
    def __init__(self, ledger_service: DailyLegerService = Depends()):
        self.ledger_service = ledger_service

    async def create_invoice(
        self, invoice_create: InvoiceCreate, session: AsyncClientSession | None = None
    ):
        invoice = Invoice(
            invoice_number=invoice_create.invoice_number,
            invoice_date=invoice_create.invoice_date,
            invoice_type=invoice_create.invoice_type,
            customer_name=invoice_create.customer_name,
            customer_address=invoice_create.customer_address,
            customer_phone=invoice_create.customer_phone,
            vehicle_number=invoice_create.vehicle_number,
            mechanic=invoice_create.mechanic,
            items=invoice_create.items,
            items_total=invoice_create.items_total,
            discount=invoice_create.discount,
            scrap_amount=invoice_create.scrap_amount,
            total_amount=invoice_create.total_amount,
            payment_status=invoice_create.payment_status,
        )
        await invoice.insert(session=session)
        return invoice

    async def get_invoices(self, params: InvoiceQueryParams):
        conditions = []

        if params.search:
            search = re.escape(params.search.strip())

            conditions.append(
                Or(
                    {"invoice_number": {"$regex": search, "$options": "i"}},
                    {"customer_name": {"$regex": search, "$options": "i"}},
                    {"customer_phone": {"$regex": search, "$options": "i"}},
                )
            )

        if params.payment_status:
            conditions.append(Invoice.payment_status == params.payment_status)

        if params.invoice_type:
            conditions.append(Invoice.invoice_type == params.invoice_type)

        query = Invoice.find(*conditions, fetch_links=True).sort(
            -Invoice.invoice_date, -Invoice.created_at
        )

        invoices, total = await paginate(query, page=params.page, size=params.size)

        return PaginatedResponse[InvoiceListResponse](
            items=[InvoiceListResponse.from_document(invoice) for invoice in invoices],
            pagination=Pagination.from_total(
                page=params.page, size=params.size, total=total
            ),
        )

    async def get_invoice(self, invoice_id: PydanticObjectId):
        invoice = await Invoice.find_one(
            Invoice.id == invoice_id, Invoice.is_active == True, fetch_links=True
        )
        if not invoice:
            raise AppException("Invoice not found.", status.HTTP_404_NOT_FOUND)

        if invoice.mechanic:
            payments = (
                await MechanicInvoicePayment.find(
                    MechanicInvoicePayment.invoice.id == invoice.id,
                    MechanicInvoicePayment.is_active == True,
                )
                .sort(-MechanicInvoicePayment.payment_date)
                .to_list()
            )
        else:
            payments = (
                await Payment.find(
                    Payment.reference_id == invoice.id,
                    Payment.reference_type == PaymentReferenceType.INVOICE,
                    Payment.is_active == True,
                )
                .sort(-Payment.payment_date)
                .to_list()
            )
        return InvoiceDetailsResponse.from_document(invoice, payments)
