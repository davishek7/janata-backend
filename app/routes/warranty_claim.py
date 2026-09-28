from fastapi import APIRouter, Depends, Query
from beanie import PydanticObjectId
from app.security.dependencies import get_current_user_id


router = APIRouter()


@router.post("/")
async def create_warranty_claim(): ...


@router.get("/")
async def get_warranty_claims(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
): ...


@router.get("/{claim_id}")
async def get_warranty_claim(claim_id: PydanticObjectId): ...
