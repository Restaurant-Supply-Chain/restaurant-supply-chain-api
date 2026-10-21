from pydantic import BaseModel, Field
from typing import Optional, Literal


class OutletCreate(BaseModel):
    restaurant_id: int = Field(gt=0, description="Associated restaurant ID")
    name: str = Field(min_length=2, max_length=100, description="Outlet branch name")
    outlet_code: str = Field(min_length=2, max_length=50, description="Unique outlet code")
    is_default: bool = False
    status: Literal["ACTIVE", "INACTIVE"] = "ACTIVE"


class OutletUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    outlet_code: Optional[str] = Field(default=None, min_length=2, max_length=50)
    is_default: Optional[bool] = None
    status: Optional[Literal["ACTIVE", "INACTIVE"]] = None


class OutletResponse(BaseModel):
    id: int
    restaurant_id: int
    name: str
    outlet_code: str
    is_default: bool
    status: str

    model_config = {"from_attributes": True}
