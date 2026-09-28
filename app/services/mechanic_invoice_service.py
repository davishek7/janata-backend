from fastapi import status, Depends
from beanie import PydanticObjectId
from decimal import Decimal
from pymongo.asynchronous.client_session import AsyncClientSession
from app.core.database import transaction
from app.exceptions.custom_exception import AppException
from app.enums.InvoiceType import InvoiceType
from app.enums.PaymentStatus import PaymentStatus
from app.models import Invoice, Mechanic, MechanicInvoicePayment, InvoiceItem
from app.services.invoice_service import InvoiceService
from app.services.counter_service import CounterService
from app.schemas.invoice_schema import InvoiceCreate
from app.schemas.mechanic_invoice_schema import (
    MechanicInvoiceCreate,
    MechanicInvoicePaymentCreate,
    MechanicInvoicePaymentResponse,
)
from app.utils.responses import success_response


class MechanicInvoiceService:
    def __init__(
        self,
        invoice_service: InvoiceService = Depends(),
        counter_service: CounterService = Depends(),
    ):
        self.invoice_service = invoice_service
        self.counter_service = counter_service

    async def create_invoice(
        self, mechanic_id: PydanticObjectId, invoice_create: MechanicInvoiceCreate
    ):
        async with transaction() as session:
            mechanic = await Mechanic.find_one(
                Mechanic.id == mechanic_id, Mechanic.is_active == True
            )
            if not mechanic:
                raise AppException("Mechanic not found.", status.HTTP_404_NOT_FOUND)

            items_total = 0
            invoice_items = []

            key = f"mechanic_invoice_{invoice_create.invoice_date.year}"
            counter = await self.counter_service.get_next_counter(key, session=session)
            invoice_number = f"BADSHA-{invoice_create.invoice_date.year}-{counter:06d}"

            for item in invoice_create.items:
                invoice_item = InvoiceItem(
                    item_type=item.item_type,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    product=item.product,
                    serial_number=item.serial_number,
                )
                invoice_items.append(invoice_item)
                items_total += item.total_amount

            total_amount = items_total - invoice_create.discount

            invoice_data = InvoiceCreate(
                invoice_number=invoice_number,
                invoice_date=invoice_create.invoice_date,
                invoice_type=InvoiceType.MECHANIC_JOB,
                customer_name=invoice_create.customer_name,
                customer_address=invoice_create.customer_address,
                customer_phone=invoice_create.customer_phone,
                vehicle_number=invoice_create.vehicle_number,
                mechanic=mechanic,
                items=invoice_items,
                items_total=items_total,
                discount=invoice_create.discount,
                total_amount=total_amount,
                payment_status=PaymentStatus.UNPAID,
            )

            invoice = await self.invoice_service.create_invoice(
                invoice_data, session=session
            )

            if invoice_create.advance_paid > 0:
                payment_schema = MechanicInvoicePaymentCreate(
                    invoice_id=invoice.id,
                    amount=invoice_create.advance_paid,
                    payment_mode=invoice_create.advance_payment_mode,
                    payment_date=invoice_create.advance_date,
                )
                await self._add_payment(invoice.id, payment_schema, session=session)

            return success_response(
                "Mechanic invoice created successfully.", status.HTTP_201_CREATED
            )

    async def add_payment(
        self,
        invoice_id: PydanticObjectId,
        payment_schema: MechanicInvoicePaymentCreate,
        session: AsyncClientSession | None = None,
    ):
        return await self._add_payment(invoice_id, payment_schema, session=session)

    async def _add_payment(
        self,
        invoice_id: PydanticObjectId,
        payment_schema: MechanicInvoicePaymentCreate,
        session: AsyncClientSession | None = None,
    ):
        invoice = await Invoice.find_one(
            Invoice.id == invoice_id, Invoice.is_active == True, session=session
        )
        if not invoice:
            raise AppException("Mechanic invoice not found.", status.HTTP_404_NOT_FOUND)

        payment = MechanicInvoicePayment(
            invoice=invoice,
            amount=payment_schema.amount,
            payment_mode=payment_schema.payment_mode,
            payment_date=payment_schema.payment_date,
            notes=payment_schema.notes,
        )
        await payment.insert(session=session)
        await self._recalculate_payment_status(
            invoice_id, payment.amount, session=session
        )

    async def _recalculate_payment_status(
        self,
        invoice_id: PydanticObjectId,
        amount: Decimal,
        session: AsyncClientSession | None = None,
    ):
        invoice = await Invoice.find_one(
            Invoice.id == invoice_id, Invoice.is_active == True, session=session
        )
        if not invoice:
            raise AppException("Mechanic invoice not found.", status.HTTP_404_NOT_FOUND)

        payments = await MechanicInvoicePayment.find(
            MechanicInvoicePayment.invoice.id == invoice.id,
            MechanicInvoicePayment.is_active == True,
            session=session,
        ).to_list()

        paid_amount = sum(
            (payment.amount for payment in payments),
            Decimal("0"),
        )

        if invoice.paid_amount == invoice.total_amount:
            raise AppException("Invoice is fully paid.", status.HTTP_400_BAD_REQUEST)

        new_paid_amount = invoice.paid_amount + amount

        if new_paid_amount > invoice.total_amount:
            raise AppException(
                "Payment exceeds invoice amount.",
                status.HTTP_400_BAD_REQUEST,
            )

        invoice.paid_amount = paid_amount

        if paid_amount <= Decimal("0"):
            invoice.payment_status = PaymentStatus.UNPAID
        elif paid_amount < invoice.total_amount:
            invoice.payment_status = PaymentStatus.PARTIAL
        else:
            invoice.payment_status = PaymentStatus.PAID

        await invoice.save(session=session)
