from pydantic import BaseModel
from beanie import PydanticObjectId
from datetime import datetime
from decimal import Decimal
from app.enums.SaleType import SaleType
from app.enums.PaymentStatus import PaymentStatus


class RecentSaleResponse(BaseModel):
    id: PydanticObjectId
    sale_type: SaleType
    reference_number: str | PydanticObjectId
    sale_date: datetime
    description: str
    payment_status: PaymentStatus
    amount: Decimal
