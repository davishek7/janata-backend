from fastapi import status
import re
from beanie import PydanticObjectId
from beanie.operators import Or
from app.models import ScrapProduct
from app.exceptions.custom_exception import AppException
from app.schemas.scrap_product_schema import (
    ScrapProductCreate,
    ScrapProductResponse,
    ScrapProductLookupResponse,
    ScrapProductQueryParams,
)
from app.utils.responses import success_response
from app.utils.pagination import paginate
from app.schemas.common.pagination_schema import Pagination, PaginatedResponse


class ScrapProductService:
    async def create_scrap_product(self, scrap_product_schema: ScrapProductCreate):
        scrap_product = ScrapProduct(
            name=scrap_product_schema.name,
            description=scrap_product_schema.description,
            purchase_price=scrap_product_schema.purchase_price,
            selling_price=scrap_product_schema.selling_price,
        )
        await scrap_product.insert()
        return success_response(
            "Scrap product added successfully.", status.HTTP_201_CREATED
        )

    async def get_scrap_products(self, params: ScrapProductQueryParams):
        conditions = []

        if params.search:
            search = re.escape(params.search.strip())
            conditions.append(
                Or(
                    {"name": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}},
                )
            )
        query = ScrapProduct.find(*conditions, ScrapProduct.is_active == True)
        scrap_products, total = await paginate(query, params.page, params.size)
        return PaginatedResponse[ScrapProductResponse](
            items=[
                ScrapProductResponse.from_document(scrap_product)
                for scrap_product in scrap_products
            ],
            pagination=Pagination.from_total(
                page=params.page, size=params.size, total=total
            ),
        )

    async def get_scrap_product(self, scrap_product_id: PydanticObjectId):
        scrap_product = await ScrapProduct.find_one(
            ScrapProduct.id == scrap_product_id, ScrapProduct.is_active == True
        )
        if not scrap_product:
            raise AppException("Scrap product not found.", status.HTTP_404_NOT_FOUND)
        return ScrapProductResponse.from_document(scrap_product)

    async def scrap_product_lookup(self):
        scrap_products = await ScrapProduct.find(
            ScrapProduct.is_active == True
        ).to_list()
        return [
            ScrapProductLookupResponse.from_document(product)
            for product in scrap_products
        ]
