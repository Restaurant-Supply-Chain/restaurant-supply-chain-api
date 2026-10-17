from typing import Literal

from pydantic import BaseModel, Field


class SalesOrderCreate(BaseModel):
    restaurant_id: int = Field(gt=0)
    supplier_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class SalesOrderResponse(BaseModel):
    id: int
    restaurant_id: int
    supplier_id: int
    quantity: int
    status: Literal["pending", "confirmed", "cancelled"]
