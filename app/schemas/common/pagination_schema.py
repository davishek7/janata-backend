from math import ceil
from typing import Generic, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel


T = TypeVar("T")


class Pagination(BaseModel):
    page: int
    size: int
    total: int
    pages: int
    has_previous: bool
    has_next: bool

    @classmethod
    def from_total(
        cls,
        *,
        page: int,
        size: int,
        total: int,
    ):
        pages = max(1, ceil(total / size))

        return cls(
            page=page,
            size=size,
            total=total,
            pages=pages,
            has_previous=page > 1,
            has_next=page < pages,
        )


class PaginatedResponse(GenericModel, Generic[T]):
    items: list[T]
    pagination: Pagination
