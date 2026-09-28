from pydantic import BaseModel, Field
from beanie import PydanticObjectId
from decimal import Decimal
from app.models import ScrapProduct
from .common.query_params import PaginationQueryParams, SearchQueryParams


class ScrapProductQueryParams(PaginationQueryParams, SearchQueryParams):
    pass


class ScrapProductCreate(BaseModel):
    name: str

    description: str | None = None

    purchase_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    selling_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class ScrapProductResponse(BaseModel):
    id: PydanticObjectId

    name: str

    description: str | None = None

    purchase_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    selling_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    stock_quantity: int

    @classmethod
    def from_document(cls, product: ScrapProduct):
        return cls(
            id=product.id,
            name=product.name,
            description=product.description,
            stock_quantity=product.stock_quantity,
            purchase_price=product.purchase_price,
            selling_price=product.selling_price,
        )


class ScrapProductLookupResponse(BaseModel):
    id: PydanticObjectId

    name: str

    @classmethod
    def from_document(cls, product: ScrapProduct):
        return cls(id=product.id, name=product.name)
