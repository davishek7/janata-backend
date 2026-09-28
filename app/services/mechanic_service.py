from fastapi import status, Depends
import re
from beanie import PydanticObjectId
from beanie.operators import Or
from pymongo.asynchronous.client_session import AsyncClientSession
from decimal import Decimal
from app.core.database import transaction
from app.models import Mechanic, MechanicLedger
from app.schemas.mechanic_schema import (
    MechanicCreate,
    MechanicResponse,
    MechanicLedgerCreate,
    MechanicLedgerResponse,
    ProductTakenCreate,
    MechanicQueryParams,
)
from app.schemas.common.pagination_schema import Pagination, PaginatedResponse
from app.utils.pagination import paginate
from app.exceptions.custom_exception import AppException
from app.utils.responses import success_response
from app.enums.MechanicLedgerType import MechanicLedgerType
from app.core.database import transaction
from app.services import DailyLegerService
from app.models import Product
from app.schemas.daily_ledger_schema import LedgerCreate
from app.enums.LedgerEntryType import LedgerEntryType
from app.enums.LedgerType import LedgerType
from pymongo.asynchronous.client_session import AsyncClientSession


class MechanicService:
    def __init__(self, daily_ledger_service: DailyLegerService = Depends()):
        self.daily_ledger_service = daily_ledger_service

    async def create_mechanic(self, mechanic_create: MechanicCreate):
        mechanic = Mechanic(
            full_name=mechanic_create.full_name, phone=mechanic_create.phone
        )
        await mechanic.insert()
        return success_response("Mechanic added successfully.", status.HTTP_201_CREATED)

    async def get_mechanics(self, params: MechanicQueryParams):
        conditions = []
        if params.search:
            search = re.escape(params.search.strip())

            conditions.append(
                Or(
                    {"full_name": {"$regex": search, "$options": "i"}},
                    {"phone": {"$regex": search, "$options": "i"}},
                )
            )
        query = Mechanic.find(*conditions, Mechanic.is_active == True)

        mechanics, total = await paginate(query, page=params.page, size=params.size)

        return PaginatedResponse[MechanicResponse](
            items=[MechanicResponse.from_document(mechanic) for mechanic in mechanics],
            pagination=Pagination.from_total(
                page=params.page, size=params.size, total=total
            ),
        )

    async def _get_mechanic(self, mechanic_id: PydanticObjectId):
        mechanic = await Mechanic.find_one(
            Mechanic.id == mechanic_id, Mechanic.is_active == True
        )
        if not mechanic:
            raise AppException("Mechanic not found.", status.HTTP_404_NOT_FOUND)
        return mechanic

    async def get_mechanic(self, mechanic_id: PydanticObjectId):
        mechanic = await self._get_mechanic(mechanic_id)
        return MechanicResponse.from_document(mechanic)

    async def deactivate_mechanic(self, mechanic_id: PydanticObjectId):
        mechanic = await self._get_mechanic(mechanic_id)
        mechanic.is_active = False
        await mechanic.save()
        return success_response(
            "Mechanic deactivated successfully.", status.HTTP_200_OK
        )

    async def create_product_taken(
        self, mechanic_id: PydanticObjectId, product_taken_create: ProductTakenCreate
    ):
        product = await Product.find_one(
            Product.id == product_taken_create.product_id, Product.is_active == True
        )
        if product.serialized:
            ...
        else:
            product.stock_quantity -= product_taken_create.quantity
            await product.save()
        mechanic_ledger = MechanicLedgerCreate(
            transaction_date=product_taken_create.transaction_date,
            transaction_type=MechanicLedgerType.PRODUCT_TAKEN,
            amount=product_taken_create.quantity * product_taken_create.selling_price,
            description=product_taken_create.description,
            reference_id=product_taken_create.sale_id,
        )
        return await self.create_ledger_entry(mechanic_id, mechanic_ledger)

    async def create_ledger_entry(
        self, mechanic_id: PydanticObjectId, ledger_create: MechanicLedgerCreate
    ):
        async with transaction() as session:
            return await self._create_ledger_entry(
                mechanic_id=mechanic_id, ledger_create=ledger_create, session=session
            )

    async def _create_ledger_entry(
        self,
        mechanic_id: PydanticObjectId,
        ledger_create: MechanicLedgerCreate,
        session: AsyncClientSession | None = None,
    ):
        mechanic = await self._get_mechanic(mechanic_id)
        last_entry = (
            await MechanicLedger.find(
                MechanicLedger.mechanic.id == mechanic_id,
                MechanicLedger.is_active == True,
                session=session,
            )
            .sort(-MechanicLedger.created_at, -MechanicLedger.id)
            .first_or_none()
        )

        prev_balance = last_entry.balance if last_entry else Decimal("0")

        if ledger_create.transaction_type in (
            MechanicLedgerType.PRODUCT_TAKEN,
            MechanicLedgerType.CASH_TAKEN,
            MechanicLedgerType.RENT_CHARGE,
        ):
            new_balance = prev_balance + ledger_create.amount

        if ledger_create.transaction_type in (
            MechanicLedgerType.LABOUR_EARNED,
            MechanicLedgerType.PAYMENT_TO_SHOP,
            MechanicLedgerType.PAYMENT_TO_MECHANIC,
        ):
            new_balance = prev_balance - ledger_create.amount

        mechanic_ledger = MechanicLedger(
            transaction_date=ledger_create.transaction_date,
            mechanic=mechanic,
            transaction_type=ledger_create.transaction_type,
            amount=ledger_create.amount,
            payment_mode=ledger_create.payment_mode,
            balance=new_balance,
            description=ledger_create.description,
            reference_id=ledger_create.reference_id,
        )

        await mechanic_ledger.insert(session=session)
        await self._create_daily_ledger(
            mechanic,
            ledger_create,
            mechanic_ledger,
            session=session,
        )
        return success_response(
            "Ledger entry created successfully.", status.HTTP_201_CREATED
        )

    async def get_mechanic_ledgers(
        self, mechanic_id: PydanticObjectId, page: int, size: int
    ):
        mechanic = await self._get_mechanic(mechanic_id)
        query = MechanicLedger.find(
            MechanicLedger.mechanic.id == mechanic.id,
            Mechanic.is_active == True,
            fetch_links=True,
        ).sort(-MechanicLedger.transaction_date, -MechanicLedger.created_at)
        mechanic_ledgers, total = await paginate(query, page=page, size=size)
        return PaginatedResponse[MechanicLedgerResponse](
            items=[
                MechanicLedgerResponse.from_document(mechanic_ledger)
                for mechanic_ledger in mechanic_ledgers
            ],
            pagination=Pagination.from_total(page=page, size=size, total=total),
        )

    async def _create_daily_ledger(
        self,
        mechanic: Mechanic,
        ledger_create: LedgerCreate,
        mechanic_ledger: MechanicLedger,
        session: AsyncClientSession,
    ):
        if ledger_create.transaction_type == MechanicLedgerType.PAYMENT_TO_SHOP:
            await self.daily_ledger_service.create_entry(
                LedgerCreate(
                    transaction_date=ledger_create.transaction_date,
                    entry_type=LedgerEntryType.INCOME,
                    ledger_type=LedgerType.MECHANIC_SETTLEMENT,
                    amount=ledger_create.amount,
                    payment_mode=ledger_create.payment_mode,
                    description=f"Payment received from {mechanic.full_name}",
                    reference_id=mechanic_ledger.id,
                ),
                session=session,
            )

        elif ledger_create.transaction_type == MechanicLedgerType.PAYMENT_TO_MECHANIC:
            await self.daily_ledger_service.create_entry(
                LedgerCreate(
                    transaction_date=ledger_create.transaction_date,
                    entry_type=LedgerEntryType.EXPENSE,
                    ledger_type=LedgerType.MECHANIC_SETTLEMENT,
                    amount=ledger_create.amount,
                    payment_mode=ledger_create.payment_mode,
                    description=f"Payment paid to {mechanic.full_name}",
                    reference_id=mechanic_ledger.id,
                ),
                session=session,
            )
