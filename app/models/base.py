from beanie import Document, Insert, Replace, Save, before_event
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator
from bson.decimal128 import Decimal128


class BaseDocument(Document):
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @before_event(Insert)
    def on_create(self):
        now = datetime.now(timezone.utc)

        self.created_at = now
        self.updated_at = now

    @before_event([Replace, Save])
    def on_update(self):
        self.updated_at = datetime.now(timezone.utc)

    @field_validator("*", mode="before")
    @classmethod
    def convert_decimal128(cls, value):
        if isinstance(value, Decimal128):
            return value.to_decimal()
        return value


class AppBaseModel(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def convert_decimal128(cls, value):
        if isinstance(value, Decimal128):
            return value.to_decimal()
        return value
