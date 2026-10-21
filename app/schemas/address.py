from pydantic import BaseModel, Field
from typing import Optional, Literal


class AddressCreate(BaseModel):
    owner_type: Literal[
        "RESTAURANT", "OUTLET", "SUPPLIER", "USER", "WAREHOUSE"
    ]
    owner_id: int = Field(gt=0, description="Owner Entity ID")
    label: Optional[str] = Field(default=None, max_length=50, description="Address label e.g. Branch, Billing")
    line1: str = Field(min_length=2, max_length=200, description="Address Line 1")
    line2: Optional[str] = Field(default=None, max_length=200)
    city: str = Field(min_length=2, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    pincode: Optional[str] = Field(default=None, max_length=10)
    country: str = Field(default="India", max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: bool = False


class AddressUpdate(BaseModel):
    label: Optional[str] = None
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: Optional[bool] = None


class AddressResponse(BaseModel):
    id: int
    owner_type: str
    owner_id: int
    label: Optional[str] = None
    line1: str
    line2: Optional[str] = None
    city: str
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: bool

    model_config = {"from_attributes": True}
