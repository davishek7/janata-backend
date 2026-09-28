from fastapi import Depends, status
import re
from beanie import PydanticObjectId
from beanie.operators import Or
from pymongo.asynchronous.client_session import AsyncClientSession
from app.core.database import transaction
from app.exceptions.custom_exception import AppException
from app.services.daily_ledger_service import DailyLegerService
from app.services.counter_service import CounterService
from app.services.staff_ledger_service import StaffLedgerService
from app.services.mechanic_service import MechanicService
from app.services.payment_service import PaymentService
from app.models import QuickSale, QuickSaleItem, Product, User, Mechanic, Payment
from app.schemas.quick_sale_schema import (
    QuickSaleCreate,
    QuickSaleList,
    QuickSaleQueryParams,
    QuickSaleDetails,
)
from app.schemas.daily_ledger_schema import LedgerCreate
from app.schemas.mechanic_schema import MechanicLedgerCreate
from app.schemas.staff_ledger_schema import StaffLedgerCreate
from app.schemas.payment_schema import PaymentCreate
from app.enums.PaymentStatus import PaymentStatus
from app.enums.StaffLedgerType import StaffLedgerType
from app.enums.PaymentDirection import PaymentDirection
from app.enums.PaymentReferenceType import PaymentReferenceType
from app.enums.LedgerEntryType import LedgerEntryType
from app.enums.LedgerType import LedgerType
from app.enums.MechanicLedgerType import MechanicLedgerType
from app.enums.LabourType import LabourType
from app.utils.pagination import paginate
from app.schemas.common.pagination_schema import PaginatedResponse, Pagination
from app.utils.responses import success_response


class QuickSaleService:
    def __init__(
        self,
        daily_ledger_service: DailyLegerService = Depends(),
        counter_service: CounterService = Depends(),
        staff_ledger_service: StaffLedgerService = Depends(),
        mechanic_service: MechanicService = Depends(),
        payment_service: PaymentService = Depends(),
    ):
        self.daily_ledger_service = daily_ledger_service
        self.counter_service = counter_service
        self.staff_ledger_service = staff_ledger_service
        self.mechanic_service = mechanic_service
        self.payment_service = payment_service

    async def create_sale(self, sale_create: QuickSaleCreate):
        async with transaction() as session:
            items_total = 0
            sale_items = []

            for item in sale_create.items:
                product = (
                    await Product.find_one(
                        Product.id == item.product_id,
                        Product.is_active == True,
                        session=session,
                    )
                    if item.product_id
                    else None
                )
                sale_item = QuickSaleItem(
                    item_type=item.item_type,
                    product=product,
                    description=item.description,
                    quantity=item.quantity,
                    selling_price=item.selling_price,
                )
                sale_items.append(sale_item)
                items_total += sale_item.total_amount

            staff = (
                await User.find_one(User.id == sale_create.staff_id, session=session)
                if sale_create.staff_id
                else None
            )
            mechanic = (
                await Mechanic.find_one(
                    Mechanic.id == sale_create.mechanic_id, session=session
                )
                if sale_create.mechanic_id
                else None
            )

            key = f"quick_sale_{sale_create.sale_date.year}"
            counter = await self.counter_service.get_next_counter(key, session=session)
            sale_number = f"QS-{sale_create.sale_date.year}-{counter:06d}"

            total_amount = (
                items_total + sale_create.labour_amount - sale_create.discount
            )

            quick_sale = QuickSale(
                sale_number=sale_number,
                sale_date=sale_create.sale_date,
                items=sale_items,
                items_total=items_total,
                discount=sale_create.discount,
                total_amount=total_amount,
                labour_amount=sale_create.labour_amount,
                labour_type=sale_create.labour_type,
                staff=staff,
                mechanic=mechanic,
                payment_status=PaymentStatus.UNPAID,
                remarks=sale_create.remarks,
            )

            await quick_sale.insert(session=session)

            for item in quick_sale.items:
                if item.product:
                    product = await Product.find_one(
                        Product.id == item.product.id, Product.is_active == True
                    )
                    product.stock_quantity -= item.quantity
                    await product.save(session=session)

            if sale_create.paid_amount > 0:
                payment_data = PaymentCreate(
                    reference_type=PaymentReferenceType.QUICK_SALE,
                    reference_id=quick_sale.id,
                    direction=PaymentDirection.RECEIVED,
                    amount=sale_create.paid_amount,
                    payment_mode=sale_create.payment_mode,
                    payment_date=sale_create.payment_date,
                    notes=f"Payment for {quick_sale.sale_number}",
                )
                await self.payment_service._create_payment(
                    payment_data, session=session
                )

            await self.daily_ledger_service.create_entry(
                ledger_schema=LedgerCreate(
                    transaction_date=quick_sale.sale_date,
                    entry_type=LedgerEntryType.INCOME,
                    ledger_type=LedgerType.CUSTOMER_PAYMENT,
                    amount=items_total - quick_sale.discount,
                    payment_mode=sale_create.payment_mode,
                    description=f"Payment received for {quick_sale.sale_number}",
                    reference_id=quick_sale.id,
                ),
                session=session,
            )
            if quick_sale.labour_type == LabourType.MECHANIC:
                await self.mechanic_service._create_ledger_entry(
                    mechanic_id=quick_sale.mechanic.id,
                    ledger_create=MechanicLedgerCreate(
                        transaction_date=quick_sale.sale_date,
                        transaction_type=MechanicLedgerType.LABOUR_EARNED,
                        amount=quick_sale.labour_amount,
                        description=f"Labour earned from {quick_sale.sale_number}",
                        reference_id=quick_sale.id,
                    ),
                    session=session,
                )
            if quick_sale.labour_type == LabourType.STAFF:
                await self.staff_ledger_service._create_entry(
                    staff_id=quick_sale.staff.id,
                    staff_ledger_create=StaffLedgerCreate(
                        transaction_date=quick_sale.sale_date,
                        transaction_type=StaffLedgerType.SERVICE_EARNING,
                        amount=quick_sale.labour_amount,
                        description=f"Service earned from {quick_sale.sale_number}",
                        reference_id=quick_sale.id,
                    ),
                    session=session,
                )
            return success_response(
                "Quick sale added successfully.", status.HTTP_201_CREATED
            )

    async def get_sales(self, params: QuickSaleQueryParams):
        conditions = []

        if params.search:
            search = re.escape(params.search.strip())

            conditions.append(
                Or(
                    {"sale_number": {"$regex": search, "$options": "i"}},
                )
            )

        if params.payment_status:
            conditions.append(QuickSale.payment_status == params.payment_status)

        query = QuickSale.find(*conditions, fetch_links=True).sort(
            -QuickSale.sale_date, -QuickSale.created_at
        )

        quick_sales, total = await paginate(query, page=params.page, size=params.size)

        return PaginatedResponse[QuickSaleList](
            items=[
                QuickSaleList.from_document(quick_sale) for quick_sale in quick_sales
            ],
            pagination=Pagination.from_total(
                page=params.page, size=params.size, total=total
            ),
        )

    async def get_sale(self, sale_id: PydanticObjectId):
        quick_sale = await QuickSale.find_one(
            QuickSale.id == sale_id, QuickSale.is_active == True, fetch_links=True
        )
        if not quick_sale:
            raise AppException("Quick sale not found.", status.HTTP_404_NOT_FOUND)
        payments = (
            await Payment.find(
                Payment.reference_type == PaymentReferenceType.QUICK_SALE,
                Payment.reference_id == sale_id,
                Payment.is_active == True,
            )
            .sort(-Payment.payment_date, -Payment.created_at)
            .to_list()
        )
        return QuickSaleDetails.from_document(quick_sale, payments)
