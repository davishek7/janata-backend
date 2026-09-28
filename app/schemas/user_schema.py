from pydantic import BaseModel, EmailStr, Field
from decimal import Decimal
from beanie import PydanticObjectId
from app.models import User
from .common.query_params import PaginationQueryParams, SearchQueryParams


class UserQueryParams(PaginationQueryParams, SearchQueryParams):
    role: str | None = None


class UserCreate(BaseModel):
    full_name: str

    email: EmailStr

    phone: str

    password: str

    monthly_salary: Decimal = Field(default=0, ge=0, max_digits=12, decimal_places=2)

    role_id: PydanticObjectId


class UserListResponse(BaseModel):
    id: PydanticObjectId

    full_name: str

    email: EmailStr

    phone: str

    role: str

    @classmethod
    def from_document(cls, user: User):
        return cls(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            role=user.role.name,
        )


class UserDetailsResponse(UserListResponse):
    email: EmailStr

    monthly_salary: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )

    @classmethod
    def from_document(cls, user: User):
        return cls(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            role=user.role.name,
            monthly_salary=user.monthly_salary,
        )
