from beanie import PydanticObjectId
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from app.enums.ProductCategory import ProductCategory
from app.enums.InventoryStatus import InventoryStatus
from app.models import Product, InventoryItem
from .common.query_params import PaginationQueryParams, SearchQueryParams


class ProductQueryParams(PaginationQueryParams, SearchQueryParams):
    serialized: bool | None = None
    category: ProductCategory | None = None


class ProductCreate(BaseModel):
    name: str

    category: ProductCategory

    serialized: bool = False

    foc_months: int | None = None

    prorata_months: int | None = None

    stock_quantity: int = 0

    purchase_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    default_selling_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    default_vendor: PydanticObjectId | None = None

    low_stock_threshold: int = 0


class ProductUpdate(BaseModel):
    name: str | None = None

    category: ProductCategory | None = None

    purchase_price: float | None = None

    default_selling_price: float | None = None

    default_vendor: PydanticObjectId | None = None

    low_stock_threshold: int | None = None

    serialized: bool | None = None

    foc_months: int | None = None

    prorata_months: int | None = None


class ProductListResponse(BaseModel):
    id: PydanticObjectId

    name: str

    category: ProductCategory

    serialized: bool

    stock_quantity: int

    @classmethod
    def from_document(cls, product: Product):
        return cls(
            id=product.id,
            name=product.name,
            category=product.category,
            serialized=product.serialized,
            stock_quantity=product.stock_quantity,
        )


class InventoryItemResponse(BaseModel):
    serial_number: str
    purchase_date: date | None = None
    purchase_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    status: InventoryStatus

    @classmethod
    def from_document(cls, inventory_item: InventoryItem):
        return cls(
            serial_number=inventory_item.serial_number,
            purchase_date=inventory_item.purchase_date,
            purchase_price=inventory_item.purchase_price,
            status=inventory_item.status,
        )


class ProducDetailsResponse(ProductListResponse):
    foc_months: int | None = None

    prorata_months: int | None = None

    purchase_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    default_selling_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    default_vendor_id: PydanticObjectId

    default_vendor_name: str

    low_stock_threshold: int

    inventory_items: list[InventoryItemResponse] = []

    @classmethod
    def from_document(cls, product: Product, items: list[InventoryItem] = None):
        return cls(
            id=product.id,
            name=product.name,
            category=product.category,
            serialized=product.serialized,
            stock_quantity=product.stock_quantity,
            foc_months=product.foc_months,
            prorata_months=product.prorata_months,
            purchase_price=product.purchase_price,
            default_selling_price=product.default_selling_price,
            default_vendor_id=product.default_vendor.id,
            default_vendor_name=product.default_vendor.vendor_name,
            low_stock_threshold=product.low_stock_threshold,
            inventory_items=[
                InventoryItemResponse.from_document(item) for item in items
            ],
        )


class ProductLookupResponse(BaseModel):
    id: PydanticObjectId
    name: str
    serialized: bool

    @classmethod
    def from_document(cls, product: Product):
        return cls(id=product.id, name=product.name, serialized=product.serialized)


class ProductInStockResponse(BaseModel):
    serial_number: str

    @classmethod
    def from_document(cls, item: InventoryItem):
        return cls(serial_number=item.serial_number)
