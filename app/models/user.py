from beanie import Indexed, Link
from pydantic import EmailStr, Field
from decimal import Decimal
from .base import BaseDocument
from .user_role import UserRole


class User(BaseDocument):
    full_name: str

    email: Indexed(EmailStr, unique=True)  # type: ignore

    phone: Indexed(str, unique=True)  # type: ignore

    hashed_password: str

    role: Link[UserRole]

    monthly_salary: Decimal | None = Field(
        default=None, gt=0, max_digits=12, decimal_places=2
    )

    class Settings:
        name = "users"
