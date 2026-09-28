from fastapi import status, Depends
import re
from beanie import PydanticObjectId
from beanie.operators import Or
from decimal import Decimal
from app.core.database import transaction
from app.models import (
    Sale,
    SaleItem,
    InvoiceItem,
    Product,
    InventoryItem,
    ScrapReceive,
    ScrapProduct,
)
from app.schemas.sale_schema import SaleCreate, SaleQueryParams
from app.exceptions.custom_exception import AppException
from app.enums.InventoryStatus import InventoryStatus
from app.enums.SaleSource import SaleSource
from app.enums.InvoiceType import InvoiceType
from app.enums.InvoiceItemType import InvoiceItemType
from app.enums.PaymentStatus import PaymentStatus
from app.enums.PaymentReferenceType import PaymentReferenceType
from app.enums.PaymentDirection import PaymentDirection
from app.services.counter_service import CounterService
from app.services.invoice_service import InvoiceService
from app.services.warranty_service import WarrantyService
from app.utils.responses import success_response
from app.schemas.sale_schema import SaleListResponse, SaleDetailsResponse
from app.schemas.common.pagination_schema import Pagination, PaginatedResponse
from app.utils.pagination import paginate
from app.schemas.warranty_schema import WarrantyCreate
from app.schemas.invoice_schema import InvoiceCreate
from app.schemas.payment_schema import PaymentCreate


class SaleService:
    def __init__(
        self,
        warranty_service: WarrantyService = Depends(),
        counter_service: CounterService = Depends(),
        invoice_service: InvoiceService = Depends(),
    ):
        self.warranty_service = warranty_service
        self.counter_service = counter_service
        self.invoice_service = invoice_service

    async def create_sale(
        self,
        sale_create_schema: SaleCreate,
    ):
        async with transaction() as session:
            sale_items = []
            scrap_items = []
            invoice_items = []
            items_total = Decimal("0")
            scrap_amount = Decimal("0")

            product_ids = [item.product_id for item in sale_create_schema.items]
            products = await Product.find(
                Product.id == {"$in": product_ids}, session=session
            ).to_list()

            if len(products) != len(product_ids):
                raise AppException(
                    "One or more products not found", status.HTTP_404_NOT_FOUND
                )
            product_map = {product.id: product for product in products}

            if sale_create_schema.scrap_received:
                scrap_product_ids = [
                    scrap_product.scrap_product_id
                    for scrap_product in sale_create_schema.scrap_received
                ]
                scrap_products = await ScrapProduct.find(
                    ScrapProduct.id == {"$in": scrap_product_ids}, session=session
                ).to_list()

                if len(scrap_products) != len(scrap_product_ids):
                    raise AppException(
                        "One or more scrap products not found",
                        status.HTTP_404_NOT_FOUND,
                    )
                scrap_product_map = {
                    scrap_product.id: scrap_product for scrap_product in scrap_products
                }

            for item in sale_create_schema.items:
                product = product_map.get(item.product_id)

                if not product:
                    raise AppException(
                        "Product not found",
                        status.HTTP_404_NOT_FOUND,
                    )
                inventory_item = await InventoryItem.find_one(
                    InventoryItem.product.id == item.product_id,
                    InventoryItem.serial_number == item.serial_number,
                    InventoryItem.status == InventoryStatus.IN_STOCK,
                    fetch_links=True,
                )

                if sale_create_schema.source == SaleSource.SYSTEM:
                    inventory_item.status = InventoryStatus.SOLD
                    await inventory_item.save(session=session)
                    product.stock_quantity -= 1
                    await product.save(session=session)

                sale_item = SaleItem(
                    product=product,
                    inventory_item=inventory_item,
                    serial_number=item.serial_number,
                    selling_price=item.selling_price,
                )

                sale_items.append(sale_item)
                items_total += item.selling_price

                if sale_create_schema.scrap_received:
                    for scrap_item in sale_create_schema.scrap_received:
                        scrap_product = scrap_product_map.get(
                            scrap_item.scrap_product_id
                        )

                        if not scrap_product:
                            raise AppException(
                                "Scrap Product not found",
                                status.HTTP_404_NOT_FOUND,
                            )
                        scrap_receive = ScrapReceive(
                            product=scrap_product,
                            quantity=scrap_item.quantity,
                            exchange_value=scrap_item.exchange_value,
                        )
                        scrap_items.append(scrap_receive)

                        scrap_product.stock_quantity += scrap_item.quantity
                        await scrap_product.save(session=session)

                        scrap_amount += scrap_item.quantity * scrap_item.exchange_value

            key = f"sale_{sale_create_schema.sale_date.year}"
            counter = await self.counter_service.get_next_counter(key, session=session)
            sale_number = f"SALE-{sale_create_schema.sale_date.year}-{counter:06d}"

            sale = Sale(
                sale_number=sale_number,
                source=sale_create_schema.source,
                customer_name=sale_create_schema.customer_name,
                customer_address=sale_create_schema.customer_address,
                customer_phone=sale_create_schema.customer_phone,
                vehicle_number=sale_create_schema.vehicle_number,
                items=sale_items,
                scrap_received=scrap_items,
                sale_date=sale_create_schema.sale_date,
                items_total=items_total,
                discount=sale_create_schema.discount,
                scrap_amount=scrap_amount,
                total_amount=items_total - sale_create_schema.discount - scrap_amount,
            )

            await sale.insert(session=session)

            key = f"sale_invoice_{sale.sale_date.year}"
            counter = await self.counter_service.get_next_counter(key, session=session)
            invoice_number = f"JANATA-{sale.sale_date.year}-{counter:06d}"

            for item in sale.items:
                invoice_item = InvoiceItem(
                    item_type=InvoiceItemType.PRODUCT,
                    description=item.product.name,
                    unit_price=item.selling_price,
                    product=item.product,
                    serial_number=item.serial_number,
                )

                invoice_items.append(invoice_item)

                warranty_data = WarrantyCreate(
                    sale_id=sale.id,
                    product_id=item.product.id,
                    sale_date=sale.sale_date,
                    current_serial_number=item.serial_number,
                )

                await self.warranty_service.create_warranty(
                    warranty_data, session=session
                )

            invoice_data = InvoiceCreate(
                invoice_number=invoice_number,
                invoice_date=sale.sale_date,
                invoice_type=InvoiceType.BATTERY_SALE,
                customer_name=sale.customer_name,
                customer_address=sale.customer_address,
                customer_phone=sale.customer_phone,
                vehicle_number=sale.vehicle_number,
                items=invoice_items,
                items_total=sale.items_total,
                discount=sale.discount,
                scrap_amount=sale.scrap_amount,
                total_amount=sale.total_amount,
                payment_status=PaymentStatus.UNPAID,
            )

            invoice = await self.invoice_service.create_invoice(
                invoice_data, session=session
            )
            sale.invoice = invoice
            await sale.save(session=session)

            if sale_create_schema.initial_payment > 0:
                payment_schema = PaymentCreate(
                    reference_type=PaymentReferenceType.INVOICE,
                    reference_id=invoice.id,
                    direction=PaymentDirection.RECEIVED,
                    amount=sale_create_schema.initial_payment,
                    payment_mode=sale_create_schema.payment_mode,
                    payment_date=sale.sale_date,
                    notes=f"Initial payment for {invoice.invoice_number}",
                )
                await self.invoice_service.add_payment(
                    invoice.id, payment_schema, session=session
                )

        return success_response("Sale created successfully.", status.HTTP_201_CREATED)

    async def get_sales(self, params: SaleQueryParams):
        conditions = []

        if params.search:
            search = re.escape(params.search.strip())

            conditions.append(
                Or(
                    {"sale_number": {"$regex": search, "$options": "i"}},
                    {"customer_name": {"$regex": search, "$options": "i"}},
                    {"customer_phone": {"$regex": search, "$options": "i"}},
                )
            )

        if params.source:
            conditions.append(Sale.source == params.source)

        if params.payment_status:
            conditions.append(Sale.invoice.payment_status == params.payment_status)

        query = Sale.find(*conditions, Sale.is_active == True, fetch_links=True).sort(
            -Sale.created_at
        )

        sales, total = await paginate(query, page=params.page, size=params.size)

        return PaginatedResponse[SaleListResponse](
            items=[SaleListResponse.from_document(sale) for sale in sales],
            pagination=Pagination.from_total(
                page=params.page, size=params.size, total=total
            ),
        )

    async def get_sale(self, sale_id: PydanticObjectId):
        sale = await Sale.find_one(
            Sale.id == sale_id, Sale.is_active == True, fetch_links=True
        )
        if not sale:
            raise AppException("Sale is not found.", status.HTTP_404_NOT_FOUND)
        return SaleDetailsResponse.from_document(sale)
