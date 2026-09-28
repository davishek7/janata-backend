from fastapi import status, Depends
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from pymongo.asynchronous.client_session import AsyncClientSession
from app.models import Warranty, Product, Sale
from app.core.database import transaction
from app.schemas.warranty_schema import WarrantyCreate
from app.enums.WarrantyStatus import WarrantyStatus
from app.exceptions.custom_exception import AppException
from app.schemas.warranty_schema import WarrantySearchResponse


class WarrantyService:
    async def create_warranty(
        self, warranty_create: WarrantyCreate, session: AsyncClientSession | None = None
    ):
        sale = await Sale.find_one(
            Sale.id == warranty_create.sale_id, Sale.is_active == True, session=session
        )
        if not sale:
            raise AppException("Sale not found.", status.HTTP_404_NOT_FOUND)
        product = await Product.find_one(
            Product.id == warranty_create.product_id,
            Product.is_active == True,
            session=session,
        )
        if not product:
            raise AppException("Product not found.", status.HTTP_404_NOT_FOUND)

        warranty = Warranty(
            sale=sale,
            product=product,
            foc_end_date=sale.sale_date
            + relativedelta(months=product.foc_months)
            - timedelta(days=1),
            prorata_end_date=sale.sale_date
            + relativedelta(months=product.foc_months)
            + relativedelta(months=product.prorata_months)
            - timedelta(days=1),
            current_serial_number=warranty_create.current_serial_number,
        )
        return await warranty.insert(session=session)

    async def search_warranty(self, serial_number: str):
        warranty = await Warranty.find_one(
            Warranty.current_serial_number == serial_number,
            Warranty.is_active == True,
            fetch_links=True,
        )
        if not warranty:
            raise AppException(
                "Warranty for the serial no is not found.", status.HTTP_404_NOT_FOUND
            )

        today = date.today()

        if today <= warranty.foc_end_date:
            warranty_status = WarrantyStatus.FOC

        elif today <= warranty.prorata_end_date:
            warranty_status = WarrantyStatus.PRORATA

        else:
            warranty_status = WarrantyStatus.EXPIRED

        months_used = (
            relativedelta(
                today,
                warranty.sale.sale_date,
            ).years
            * 12
            + relativedelta(
                today,
                warranty.sale.sale_date,
            ).months
        )
        return WarrantySearchResponse.from_document(
            warranty, warranty_status, months_used=months_used
        )
