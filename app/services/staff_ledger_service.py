from fastapi import status, Depends
from beanie import PydanticObjectId
from decimal import Decimal
from pymongo.asynchronous.client_session import AsyncClientSession
from app.core.database import transaction
from app.models import StaffLedger, User
from app.schemas.staff_ledger_schema import StaffLedgerResponse, StaffLedgerCreate
from app.enums.StaffLedgerType import StaffLedgerType
from app.exceptions.custom_exception import AppException
from .user_service import UserService
from app.utils.pagination import paginate
from app.schemas.common.pagination_schema import Pagination, PaginatedResponse


class StaffLedgerService:
    def __init__(self, user_service: UserService = Depends()):
        self.user_service = user_service

    async def get_staff_ledgers(self, staff_id: PydanticObjectId, page: int, size: int):
        staff = await User.find_one(
            User.id == staff_id,
            User.is_active == True,
            User.role.name == "COUNTER_STAFF",
            fetch_links=True,
        )
        if not staff:
            raise AppException("Staff not found.", status.HTTP_404_NOT_FOUND)
        query = StaffLedger.find(
            StaffLedger.staff.id == staff.id, StaffLedger.is_active == True
        ).sort(-StaffLedger.created_at, -StaffLedger.id)
        ledgers, total = await paginate(query, page, size)
        return PaginatedResponse[StaffLedgerResponse](
            items=[StaffLedgerResponse.from_document(ledger) for ledger in ledgers],
            pagination=Pagination.from_total(page=page, size=size, total=total),
        )

    async def create_entry(
        self, staff_id: PydanticObjectId, staff_ledger_create: StaffLedgerCreate
    ):
        async with transaction() as session:
            return await self._create_entry(
                staff_id=staff_id,
                staff_ledger_create=staff_ledger_create,
                session=session,
            )

    async def _create_entry(
        self,
        staff_id: PydanticObjectId,
        staff_ledger_create: StaffLedgerCreate,
        session: AsyncClientSession | None = None,
    ):
        staff = await User.find_one(
            User.id == staff_id,
            User.role.name == "COUNTER_STAFF",
            User.is_active == True,
            fetch_links=True,
            session=session,
        )
        if not staff:
            raise AppException("Staff not found.", status.HTTP_404_NOT_FOUND)
        if (
            staff_ledger_create.transaction_type != StaffLedgerType.ADJUSTMENT
            and staff_ledger_create.amount <= 0
        ):
            raise AppException("Amount must be positive.", status.HTTP_400_BAD_REQUEST)

        if (
            staff_ledger_create.transaction_type == StaffLedgerType.ADJUSTMENT
            and staff_ledger_create.amount == 0
        ):
            raise AppException("Amount can not be zero.", status.HTTP_400_BAD_REQUEST)

        last_ledger = (
            await StaffLedger.find(StaffLedger.is_active == True, session=session)
            .sort(-StaffLedger.created_at)
            .first_or_none()
        )
        previous_balance = last_ledger.balance if last_ledger else Decimal("0")

        new_balance = previous_balance + staff_ledger_create.amount

        staff_ledger_entry = StaffLedger(
            transaction_date=staff_ledger_create.transaction_date,
            staff=staff,
            transaction_type=staff_ledger_create.transaction_type,
            amount=staff_ledger_create.amount,
            balance=new_balance,
            description=staff_ledger_create.description,
            reference_id=staff_ledger_create.reference_id,
        )
        await staff_ledger_entry.insert(session=session)
