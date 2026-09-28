from fastapi import Depends, status
import re
from beanie import PydanticObjectId
from beanie.operators import Or
from decimal import Decimal
from app.models import ScrapProduct, ScrapPurchase, ScrapPurchaseItem
from app.schemas.scrap_purchase_schema import (
    ScrapPurchaseCreate,
    ScrapPurchaseListResponse,
    ScrapPurchaseDetailsResponse,
    ScrapPurchaseQueryParams,
)
from app.schemas.daily_ledger_schema import LedgerCreate
from app.enums.LedgerEntryType import LedgerEntryType
from app.enums.LedgerType import LedgerType
from .daily_ledger_service import DailyLegerService
from app.core.database import transaction
from app.exceptions.custom_exception import AppException
from app.utils.responses import success_response
from app.schemas.common.pagination_schema import Pagination, PaginatedResponse
from app.utils.pagination import paginate
from app.enums.PaymentStatus import PaymentStatus
from .counter_service import CounterService


class ScrapPurchaseService:
    def __init__(
        self,
        daily_ledger_service: DailyLegerService = Depends(),
        counter_service: CounterService = Depends(),
    ):
        self.daily_ledger_service = daily_ledger_service
        self.counter_service = counter_service

    async def create_purchase(self, purchase_create: ScrapPurchaseCreate):
        async with transaction() as session:
            total_amount = Decimal("0")
            scrap_items = []

            for item in purchase_create.scrap_items:
                scrap_product = await ScrapProduct.find_one(
                    ScrapProduct.id == item.product_id,
                    ScrapProduct.is_active == True,
                    session=session,
                )
                if not scrap_product:
                    raise AppException(
                        "Scrap product not found.", status.HTTP_404_NOT_FOUND
                    )
                total_amount += item.quantity * item.purchase_price
                scrap_items.append(
                    ScrapPurchaseItem(
                        product=scrap_product,
                        quantity=item.quantity,
                        purchase_price=item.purchase_price,
                    )
                )

            key = f"scrap_purchase_{purchase_create.transaction_date.year}"
            counter = await self.counter_service.get_next_counter(key, session=session)
            purchase_number = (
                f"SP-{purchase_create.transaction_date.year}-{counter:06d}"
            )

            scrap_purchase = ScrapPurchase(
                purchase_number=purchase_number,
                transaction_date=purchase_create.transaction_date,
                scrap_items=scrap_items,
                total_amount=total_amount,
                paid_amount=purchase_create.paid_amount,
                payment_status=PaymentStatus.UNPAID,
                payment_mode=purchase_create.payment_mode,
            )
            await scrap_purchase.insert(session=session)
            for item in scrap_purchase.scrap_items:
                product = ScrapProduct.find_one(
                    ScrapProduct.id == item.product.id, ScrapProduct.is_active == True
                )
                product += item.quantity
                await product.save(session=session)

            await self.daily_ledger_service.create_entry(
                LedgerCreate(
                    transaction_date=scrap_purchase.transaction_date,
                    entry_type=LedgerEntryType.EXPENSE,
                    ledger_type=LedgerType.SCRAP_PURCHASE,
                    amount=scrap_purchase.total_amount,
                    payment_mode=scrap_purchase.payment_mode,
                ),
                session=session,
            )
            return success_response(
                "Scrap purchase added successfully.", status.HTTP_201_CREATED
            )

    async def get_purchases(self, params: ScrapPurchaseQueryParams):
        conditions = []
        if params.search:
            search = re.escape(params.search.strip())

            conditions.append(
                Or(
                    {"seller_name": {"$regex": search, "$options": "i"}},
                    {"seller_phone": {"$regex": search, "$options": "i"}},
                    {"seller_address": {"$regex": search, "$options": "i"}},
                )
            )
        if params.payment_status:
            conditions.append(ScrapPurchase.payment_status == params.payment_status)

        if params.payment_mode:
            conditions.append(ScrapPurchase.payment_mode == params.payment_mode)

        query = ScrapPurchase.find(*conditions, ScrapPurchase.is_active == True)
        purchases, total = await paginate(query, params.page, params.size)
        return PaginatedResponse[ScrapPurchaseListResponse](
            items=[
                ScrapPurchaseListResponse.from_document(purchase)
                for purchase in purchases
            ],
            pagination=Pagination.from_total(
                page=params.page, size=params.size, total=total
            ),
        )

    async def get_purchase(self, purchase_id: PydanticObjectId):
        purchase = await ScrapPurchase.find_one(
            ScrapPurchase.id == purchase_id,
            ScrapPurchase.is_active == True,
            fetch_links=True,
        )
        if not purchase:
            raise AppException("Scrap purchase not found.", status.HTTP_404_NOT_FOUND)
        return ScrapPurchaseDetailsResponse.from_document(purchase)
