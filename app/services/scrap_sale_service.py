from fastapi import status, Depends
import re
from beanie import PydanticObjectId
from beanie.operators import Or
from decimal import Decimal
from app.core.database import transaction
from app.models import ScrapSale, Payment, ScrapSaleItem, ScrapProduct
from app.schemas.scrap_sale_schema import ScrapSaleCreate
from app.schemas.payment_schema import PaymentCreate
from app.services.counter_service import CounterService
from app.services.payment_service import PaymentService
from app.enums.PaymentStatus import PaymentStatus
from app.enums.PaymentDirection import PaymentDirection
from app.enums.PaymentMode import PaymentMode
from app.enums.PaymentReferenceType import PaymentReferenceType
from app.utils.pagination import paginate
from app.schemas.common.pagination_schema import PaginatedResponse, Pagination
from app.utils.responses import success_response


class ScrapSaleService:
    def __init__(
        self,
        counter_service: CounterService = Depends(),
        payment_service: PaymentService = Depends(),
    ):
        self.counter_service = counter_service
        self.payment_service = payment_service

    async def create_sale(self, sale_create: ScrapSaleCreate):
        async with transaction() as session:
            total_amount = 0
            sale_items = []

            for item in sale_create.items:
                product = (
                    await ScrapProduct.find_one(
                        ScrapProduct.id == item.product_id,
                        ScrapProduct.is_active == True,
                        session=session,
                    )
                    if item.product_id
                    else None
                )
                sale_item = ScrapSaleItem(
                    item_type=item.item_type,
                    product=product,
                    description=item.description,
                    quantity=item.quantity,
                    weight=item.weight,
                    selling_price=item.selling_price,
                )
                sale_items.append(sale_item)
                total_amount += sale_item.total_amount

            key = f"scrap_sale_{sale_create.transaction_date.year}"
            counter = await self.counter_service.get_next_counter(key, session=session)
            sale_number = f"SS-{sale_create.transaction_date.year}-{counter:06d}"

            scrap_sale = ScrapSale(
                sale_number=sale_number,
                transaction_date=sale_create.transaction_date,
                buyer_name=sale_create.buyer_name,
                items=sale_items,
                total_amount=total_amount,
                payment_status=PaymentStatus.UNPAID,
            )
            await scrap_sale.insert(session=session)

            for item in scrap_sale.items:
                if item.product:
                    scrap_product = await ScrapProduct.find_one(
                        ScrapProduct.id == item.product.id,
                        ScrapProduct.is_active == True,
                        session=session,
                    )
                    scrap_product.stock_quantity -= item.quantity
                    await scrap_product.save(session=session)

            if sale_create.paid_amount > 0:
                payment_data = PaymentCreate(
                    reference_type=PaymentReferenceType.SCRAP_SALE,
                    reference_id=scrap_sale.id,
                    direction=PaymentDirection.RECEIVED,
                    amount=sale_create.paid_amount,
                    payment_mode=sale_create.payment_mode,
                    payment_date=sale_create.payment_date,
                    notes=f"",
                )
                await self.payment_service._create_payment(
                    payment_data, session=session
                )
