from beanie import Link
from datetime import datetime
from uuid import UUID
from .base import BaseDocument
from .user import User


class RefreshToken(BaseDocument):
    jti: str  # JWT ID stored as a standard field
    user: Link[User]
    revoked: bool = False
    expires_at: datetime

    class Settings:
        name = "refresh_tokens"
        indexes = [
            "jti",  # Index jti for fast O(1) token lookups
        ]
