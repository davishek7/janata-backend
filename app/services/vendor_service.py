from fastapi import status
import re
from beanie import PydanticObjectId
from beanie.operators import Or
from app.models import Vendor, VendorLedger
from app.exceptions.custom_exception import AppException
from app.schemas.common.pagination_schema import PaginatedResponse, Pagination
from app.schemas.vendor_schema import (
    VendorResponse,
    VendorCreate,
    VendorUpdate,
    VendorLookupResponse,
    VendorQueryParams,
    VendorLedgerResponse,
    VendorLedgerQueryParams,
)
from app.utils.pagination import paginate
from app.utils.responses import success_response
from app.enums.VendorLedgerType import VendorLedgerType


class VendorService:
    async def create_vendor(self, vendor_create_schema: VendorCreate):
        vendor_data = vendor_create_schema.model_dump(exclude_unset=True)
        vendor = Vendor(
            vendor_name=vendor_data.get("vendor_name"),
            address=vendor_data.get("address"),
            phone=vendor_data.get("phone"),
            contact_person=vendor_data.get("contact_person"),
            contact_person_phone=vendor_data.get("contact_person_phone"),
        )
        await vendor.insert()
        return success_response("Vendor created successfully", status.HTTP_201_CREATED)

    async def get_vendors(self, params: VendorQueryParams):
        conditions = []
        if params.search:
            search = re.escape(params.search.strip())

            conditions.append(
                Or(
                    {"vendor_name": {"$regex": search, "$options": "i"}},
                    {"address": {"$regex": search, "$options": "i"}},
                    {"phone": {"$regex": search, "$options": "i"}},
                    {"contact_person": {"$regex": search, "$options": "i"}},
                    {"contact_person_phone": {"$regex": search, "$options": "i"}},
                )
            )

        query = Vendor.find(*conditions, Vendor.is_active == True)
        vendors, total = await paginate(query, page=params.page, size=params.size)
        return PaginatedResponse[VendorResponse](
            items=[VendorResponse.from_document(vendor) for vendor in vendors],
            pagination=Pagination.from_total(
                page=params.page, size=params.size, total=total
            ),
        )

    async def get_vendor(self, vendor_id: PydanticObjectId):
        vendor = await Vendor.find_one(Vendor.id == vendor_id, Vendor.is_active == True)
        if not vendor:
            raise AppException("Vendor not found.", status.HTTP_404_NOT_FOUND)
        return VendorResponse.from_document(vendor)

    async def vendor_lookup(self):
        vendors = await Vendor.find(Vendor.is_active == True).to_list()
        return [VendorLookupResponse.from_document(vendor) for vendor in vendors]

    async def get_vendor_ledgers(
        self, vendor_id: PydanticObjectId, params: VendorLedgerQueryParams
    ):
        vendor = await Vendor.find_one(Vendor.id == vendor_id, Vendor.is_active == True)
        if not vendor:
            raise AppException("Vendor not found.", status.HTTP_404_NOT_FOUND)
        conditions = []
        if params.search:
            search = re.escape(params.search.strip())

            conditions.append(
                Or(
                    {"amount": {"$regex": search, "$options": "i"}},
                    {"balance": {"$regex": search, "$options": "i"}},
                    {"remarks": {"$regex": search, "$options": "i"}},
                )
            )
        if params.ledger_type:
            conditions.append(VendorLedger.ledger_type == params.ledger_type)

        query = VendorLedger.find(
            *conditions, VendorLedger.vendor.id == vendor.id
        ).sort(-VendorLedger.created_at, VendorLedger.id)
        ledgers, total = await paginate(query, page=params.page, size=params.size)
        return PaginatedResponse[VendorLedgerResponse](
            items=[VendorLedgerResponse.from_document(ledger) for ledger in ledgers],
            pagination=Pagination.from_total(
                page=params.page, size=params.size, total=total
            ),
        )
