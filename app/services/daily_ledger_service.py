from fastapi import status
from decimal import Decimal
from pymongo.asynchronous.client_session import AsyncClientSession
from app.utils.responses import success_response
from app.models import LedgerEntry
from app.schemas.daily_ledger_schema import LedgerCreate
from app.enums.LedgerEntryType import LedgerEntryType


class DailyLegerService:
    async def create_entry(
        self, ledger_schema: LedgerCreate, session: AsyncClientSession | None = None
    ):
        last_entry = (
            await LedgerEntry.find(LedgerEntry.is_active == True, session=session)
            .sort(-LedgerEntry.created_at)
            .first_or_none()
        )
        previous_balance = last_entry.balance if last_entry else Decimal("0")

        if ledger_schema.entry_type == LedgerEntryType.INCOME:
            new_balance = previous_balance + ledger_schema.amount
        else:
            new_balance = previous_balance - ledger_schema.amount

        ledger_create_data = ledger_schema.model_dump(exclude_unset=True)
        ledger_create_data["balance"] = new_balance

        ledger_entry = LedgerEntry(
            transaction_date=ledger_create_data.get("transaction_date"),
            entry_type=ledger_create_data.get("entry_type"),
            ledger_type=ledger_create_data.get("ledger_type"),
            amount=ledger_create_data.get("amount"),
            payment_mode=ledger_create_data.get("payment_mode"),
            balance=ledger_create_data.get("balance"),
            description=ledger_create_data.get("description"),
            reference_id=ledger_create_data.get("reference_id"),
        )

        await ledger_entry.insert(session=session)
        return success_response(
            "Daily ledger created successfully.", status.HTTP_201_CREATED
        )

    async def create_opening_balance(
        self, session: AsyncClientSession | None = None
    ): ...
