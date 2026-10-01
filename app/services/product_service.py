from fastapi import status
import re
from beanie import PydanticObjectId
from beanie.operators import Or
from app.models import Product, InventoryItem
from app.exceptions.custom_exception import AppException
from app.schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductListResponse,
    ProducDetailsResponse,
    ProductLookupResponse,
    ProductQueryParams,
    ProductInStockResponse,
)
from app.utils.responses import success_response
from app.schemas.common.pagination_schema import PaginatedResponse, Pagination
from app.utils.pagination import paginate
from app.enums.InventoryStatus import InventoryStatus


class ProductService:
    async def create_product(self, product_create_schema: ProductCreate):
        product_data = product_create_schema.model_dump(exclude_unset=True)
        product = Product(**product_data)
        await product.insert()
        return success_response(
            "Product created successfully.", status.HTTP_201_CREATED
        )

    async def get_products(self, params: ProductQueryParams):
        conditions = []

        if params.search:
            search = re.escape(params.search.strip())

            conditions.append(
                Or(
                    {"name": {"$regex": search, "$options": "i"}},
                    {"default_vendor.vendor_name": {"$regex": search, "$options": "i"}},
                )
            )

        if params.serialized is not None:
            conditions.append(Product.serialized == params.serialized)

        if params.category:
            conditions.append(Product.category == params.category)

        query = Product.find(*conditions, Product.is_active == True, fetch_links=True)

        products, total = await paginate(query, params.page, params.size)

        return PaginatedResponse[ProductListResponse](
            items=[ProductListResponse.from_document(product) for product in products],
            pagination=Pagination.from_total(
                page=params.page, size=params.size, total=total
            ),
        )

    async def get_product(self, product_id: PydanticObjectId):
        product = await Product.find_one(
            Product.id == product_id, Product.is_active == True, fetch_links=True
        )
        if not product:
            raise AppException("Product not found", status.HTTP_404_NOT_FOUND)
        inventory_items = []
        if product.serialized:
            inventory_items = await InventoryItem.find(
                InventoryItem.product.id == product.id,
                InventoryItem.status == InventoryStatus.IN_STOCK,
                InventoryItem.is_active == True,
                fetch_links=True,
            ).to_list()

        return ProducDetailsResponse.from_document(product, inventory_items)

    async def update_product(
        self, product_id: PydanticObjectId, product_update_schema: ProductUpdate
    ):
        product = await Product.find_one(Product.id == product_id, fetch_links=True)
        if not product:
            raise AppException("Product not found", status.HTTP_404_NOT_FOUND)
        await product.set(product_update_schema.model_dump(exclude_unset=True))
        return success_response("Product updated successfully", status.HTTP_200_OK)

    async def product_lookup(self):
        products = await Product.find(
            Product.is_active == True, fetch_links=True
        ).to_list()
        return [ProductLookupResponse.from_document(product) for product in products]

    async def get_in_stock_serials(self, product_id: PydanticObjectId):
        product = await Product.find_one(
            Product.id == product_id,
            Product.is_active == True,
            Product.serialized == True,
        )
        if not product:
            raise AppException("Product not found.", status.HTTP_404_NOT_FOUND)
        inventory_items = await InventoryItem.find(
            InventoryItem.product.id == product.id,
            InventoryItem.is_active == True,
            InventoryItem.status == InventoryStatus.IN_STOCK,
        ).to_list()
        return [
            ProductInStockResponse.from_document(inventory_item)
            for inventory_item in inventory_items
        ]
