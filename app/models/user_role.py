from beanie import Link
from .base import BaseDocument
from app.enums.Permission import Permission


class UserRole(BaseDocument):
    name: str

    is_superuser: bool = False

    permissions: list[Permission]

    class Settings:
        name = "user_roles"
