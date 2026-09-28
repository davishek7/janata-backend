from pydantic import BaseModel
from datetime import date
from beanie import PydanticObjectId
from app.enums.WarrantyStatus import WarrantyStatus
from app.models import Warranty


class WarrantyCreate(BaseModel):
    sale_id: PydanticObjectId

    product_id: PydanticObjectId

    sale_date: date

    current_serial_number: str


class WarrantySearchResponse(BaseModel):
    id: PydanticObjectId
    # Sale Details
    customer_name: str
    customer_phone: str | None
    sale_date: date
    sale_id: PydanticObjectId

    # Battery
    product_name: str
    original_serial_number: str | None = None
    current_serial_number: str

    # Warranty
    warranty_status: WarrantyStatus

    foc_end_date: date | None

    months_used: int | None
    total_warranty_months: int | None

    prorata_end_date: date | None

    @classmethod
    def from_document(
        cls,
        warranty: Warranty,
        warranty_status: WarrantyStatus,
        months_used: int = None,
    ):
        return cls(
            id=warranty.id,
            customer_name=warranty.sale.customer_name,
            customer_phone=warranty.sale.customer_phone,
            sale_date=warranty.sale.sale_date,
            sale_id=warranty.sale.id,
            product_name=warranty.product.name,
            original_serial_number=warranty.original_serial_number,
            current_serial_number=warranty.current_serial_number,
            warranty_status=warranty_status,
            foc_end_date=warranty.foc_end_date,
            months_used=months_used,
            total_warranty_months=warranty.product.foc_months
            + warranty.product.prorata_months,
            prorata_end_date=warranty.prorata_end_date,
        )
