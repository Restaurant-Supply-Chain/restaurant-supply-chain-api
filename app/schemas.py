
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal


# User Schema
class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr


# Restaurant Schema
class RestaurantCreate(BaseModel):
    owner_user_id: int = Field(gt=0)
    name: str = Field(min_length=2, max_length=120)
    legal_name: Optional[str] = None
    cuisine_type: str
    gst_no: Optional[str] = Field(
        default=None,
        pattern=r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$"
    )
    fssai_no: Optional[str] = Field(
        default=None,
        pattern=r"^[0-9]{14}$"
    )
    contact_email: EmailStr
    contact_phone: str
    logo_url: Optional[str] = None
    status: Literal["ACTIVE", "INACTIVE", "SUSPENDED"] = "ACTIVE"
    credit_limit: float = Field(default=0, ge=0)
    payment_terms_days: int = Field(default=0, ge=0)


class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    legal_name: Optional[str] = None
    cuisine_type: Optional[str] = None
    gst_no: Optional[str] = Field(
        default=None,
        pattern=r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$"
    )
    fssai_no: Optional[str] = Field(
        default=None,
        pattern=r"^[0-9]{14}$"
    )
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    logo_url: Optional[str] = None
    status: Optional[Literal["ACTIVE", "INACTIVE", "SUSPENDED"]] = None
    credit_limit: Optional[float] = Field(default=None, ge=0)
    payment_terms_days: Optional[int] = Field(default=None, ge=0)


# Outlet Schema
class OutletCreate(BaseModel):
    restaurant_id: int = Field(gt=0)
    name: str
    outlet_code: str
    is_default: bool = False
    status: Literal["ACTIVE", "INACTIVE"] = "ACTIVE"


class OutletUpdate(BaseModel):
    name: Optional[str] = None
    outlet_code: Optional[str] = None
    is_default: Optional[bool] = None
    status: Optional[Literal["ACTIVE", "INACTIVE"]] = None


# Address Schema
class AddressCreate(BaseModel):
    owner_type: Literal[
        "RESTAURANT", "OUTLET", "SUPPLIER", "USER", "WAREHOUSE"
    ]
    owner_id: int = Field(gt=0)
    label: str
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    pincode: str
    country: str = "India"
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


# Restaurant Staff Schema
class StaffCreate(BaseModel):
    restaurant_id: int = Field(gt=0)
    user_id: int = Field(gt=0)
    role: str = "STAFF"


# Approval Request Schema
class ApprovalCreate(BaseModel):
    restaurant_id: int = Field(gt=0)
    requested_by: int = Field(gt=0)
    request_type: str
    remarks: Optional[str] = None
