from pymongo import AsyncMongoClient
from beanie import init_beanie
from contextlib import asynccontextmanager
from app.models import (
    User,
    UserRole,
    Product,
    RefreshToken,
    Sale,
    InventoryItem,
    Invoice,
    LedgerEntry,
    Mechanic,
    MechanicLedger,
    Purchase,
    ScrapSale,
    StaffLedger,
    Vendor,
    VendorLedger,
    Warranty,
    WarrantyClaim,
    Counter,
    ScrapProduct,
    ScrapPurchase,
    Payment,
    MechanicInvoicePayment,
    QuickSale,
)
from app.core.settings import settings


client = AsyncMongoClient(settings.MONGO_URL)
db = client[settings.DB_NAME]


async def init_db():
    await init_beanie(
        database=db,
        document_models=[
            User,
            UserRole,
            Product,
            RefreshToken,
            Sale,
            InventoryItem,
            Invoice,
            LedgerEntry,
            Mechanic,
            MechanicLedger,
            Purchase,
            ScrapSale,
            StaffLedger,
            Vendor,
            VendorLedger,
            Warranty,
            WarrantyClaim,
            Counter,
            ScrapProduct,
            ScrapPurchase,
            Payment,
            MechanicInvoicePayment,
            QuickSale,
        ],
    )


@asynccontextmanager
async def transaction():
    async with client.start_session() as session:
        await session.start_transaction()

        try:
            yield session
        except Exception:
            await session.abort_transaction()
            raise
        else:
            await session.commit_transaction()
