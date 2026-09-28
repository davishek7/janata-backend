from pydantic import BaseModel, Field


class PaginationQueryParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


class SearchQueryParams(BaseModel):
    search: str | None = None
