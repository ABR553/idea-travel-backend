from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PriceRange(BaseModel):
    from_price: float = Field(serialization_alias="from")
    to: float
    currency: str


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")
