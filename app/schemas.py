from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal


# Restaurant Schema-----------------
class RestaurantCreate(BaseModel):
    owner_user_id: int = Field(gt=0)
    name: str = Field(min_length=2, max_length=120)
    legal_name: Optional[str] = None
    cuisine_type: str
    gst_no: Optional[str] = None
    fssai_no: Optional[str] = None
    contact_email: EmailStr
    contact_phone: str
    status: Literal["ACTIVE", "INACTIVE", "SUSPENDED"] = "ACTIVE"
    credit_limit: float = Field(default=0, ge=0)
    payment_terms_days: int = Field(default=0, ge=0)


# Outlet Schema----------------
class OutletCreate(BaseModel):
    restaurant_id: int = Field(gt=0)
    name: str
    outlet_code: str
    is_default: bool = False
    status: Literal["ACTIVE", "INACTIVE"] = "ACTIVE"


# Address Schema-------------------
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
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: bool = False

    # Restaurant Staff ------------------

class RestaurantStaffCreate(BaseModel):
    restaurant_id: int = Field(gt=0)
    user_id: int = Field(gt=0)
    role: Literal["OWNER", "MANAGER", "STAFF"]
    status: Literal["ACTIVE", "INACTIVE"] = "ACTIVE"


# Approval Request ------------------

class ApprovalRequestCreate(BaseModel):
    restaurant_id: int = Field(gt=0)
    requested_by: int = Field(gt=0)
    request_type: str = Field(min_length=2, max_length=100)
    description: str
    status: Literal["PENDING", "APPROVED", "REJECTED"] = "PENDING"



