from app.models import (
    Purchase,
    InventoryItem,
    Product,
    Vendor,
    PurchaseItem,
    VendorLedger,
    LedgerEntry,
)
from fastapi import status, Depends
import re
from beanie import PydanticObjectId
from beanie.operators import Or
from decimal import Decimal
from app.schemas.purchase_schema import (
    PurchaseCreate,
    PurchaseListResponse,
    PurchaseDetailsResponse,
    PurchaseQueryParams,
)
from app.exceptions.custom_exception import AppException
from app.core.database import transaction
from app.enums.VendorLedgerType import VendorLedgerType
from app.utils.responses import success_response
from app.utils.pagination import paginate
from app.schemas.common.pagination_schema import Pagination, PaginatedResponse
from .counter_service import CounterService


class PurchaseService:
    def __init__(self, counter_service: CounterService = Depends()):
        self.counter_service = counter_service

    async def create_purchase(
        self, purchase_schema: PurchaseCreate, vendor_id: PydanticObjectId
    ):
        async with transaction() as session:
            vendor = await Vendor.get(
                vendor_id,
                session=session,
            )
            if not vendor:
                raise AppException(
                    "Vendor not found",
                    status.HTTP_404_NOT_FOUND,
                )

            purchase_items = []
            validated_products = []
            total = Decimal("0")

            product_ids = [item.product_id for item in purchase_schema.items]
            products = await Product.find(
                Product.id == {"$in": product_ids}, session=session
            ).to_list()

            if len(products) != len(product_ids):
                raise AppException(
                    "One or more products not found", status.HTTP_404_NOT_FOUND
                )
            product_map = {product.id: product for product in products}

            for item in purchase_schema.items:
                product = product_map.get(item.product_id)

                if not product:
                    raise AppException(
                        "Product not found",
                        status.HTTP_404_NOT_FOUND,
                    )

                if item.quantity <= 0:
                    raise AppException("Quantity must be greater than zero.")

                if product.serialized:
                    if len(item.serial_numbers) != item.quantity:
                        raise AppException(
                            f"{product.name}: Quantity and serial numbers do not match."
                        )

                    # Duplicate serials in request
                    if len(item.serial_numbers) != len(set(item.serial_numbers)):
                        raise AppException(
                            f"{product.name}: Duplicate serial numbers found."
                        )

                    # Duplicate serials in database
                    for serial in item.serial_numbers:
                        exists = await InventoryItem.find_one(
                            InventoryItem.serial_number == serial,
                            session=session,
                        )

                        if exists:
                            raise AppException(
                                f"Serial number '{serial}' already exists."
                            )

                purchase_items.append(
                    PurchaseItem(
                        product=product,
                        quantity=item.quantity,
                        purchase_price=item.purchase_price,
                    )
                )

                validated_products.append((product, item))

                total += item.quantity * item.purchase_price

            key = f"purchase_{purchase_schema.purchase_date.year}"
            counter = await self.counter_service.get_next_counter(key, session=session)
            purchase_number = f"PUR-{purchase_schema.purchase_date.year}-{counter:06d}"

            purchase = Purchase(
                purchase_number=purchase_number,
                vendor=vendor,
                purchase_date=purchase_schema.purchase_date,
                invoice_number=purchase_schema.invoice_number,
                items=purchase_items,
                total_amount=total,
            )

            await purchase.insert(session=session)

            for product, item in validated_products:
                product.stock_quantity += item.quantity

                await product.save(session=session)

                if product.serialized:
                    inventory_items = [
                        InventoryItem(
                            product=product,
                            serial_number=serial,
                            purchase_date=item.purchase_date,
                            purchase_price=item.purchase_price,
                        )
                        for serial in item.serial_numbers
                    ]

                    await InventoryItem.insert_many(
                        inventory_items,
                        session=session,
                    )

            last_entry = (
                await VendorLedger.find(VendorLedger.vendor == vendor)
                .sort(-VendorLedger.created_at)
                .first_or_none()
            )

            current_balance = last_entry.balance if last_entry else Decimal("0")

            new_balance = current_balance - total

            purchase_entry = VendorLedger(
                transaction_date=purchase.purchase_date,
                vendor=vendor,
                ledger_type=VendorLedgerType.PURCHASE,
                amount=total,
                balance=new_balance,
                remarks=f"Purchase {purchase.invoice_number or purchase.id}",
            )

            await purchase_entry.insert(session=session)
            return success_response("Purchase added successfully.", status.HTTP_200_OK)

    async def get_purchases(
        self, vendor_id: PydanticObjectId, params: PurchaseQueryParams
    ):
        vendor = await Vendor.find_one(Vendor.id == vendor_id)

        conditions = []
        if params.search:
            search = re.escape(params.search.strip())

            conditions.append(
                Or(
                    {"purchase_number": {"$regex": search, "$options": "i"}},
                    {"invoice_number": {"$regex": search, "$options": "i"}},
                )
            )

        query = Purchase.find(
            *conditions,
            Purchase.vendor.id == vendor.id,
            Purchase.is_active == True,
            fetch_links=True,
        ).sort(-Purchase.created_at)
        purchases, total = await paginate(query, params.page, params.size)

        return PaginatedResponse[PurchaseListResponse](
            items=[
                PurchaseListResponse.from_document(purchase) for purchase in purchases
            ],
            pagination=Pagination.from_total(
                page=params.page, size=params.size, total=total
            ),
        )

    async def get_purchase(self, purchase_id: PydanticObjectId):
        purchase = await Purchase.find_one(Purchase.id == purchase_id, fetch_links=True)

        if not purchase:
            raise AppException("Purchase not found.", status.HTTP_404_NOT_FOUND)

        return PurchaseDetailsResponse.from_document(purchase)
