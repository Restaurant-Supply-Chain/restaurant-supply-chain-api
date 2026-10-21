from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal


class RestaurantCreate(BaseModel):
    owner_user_id: int = Field(gt=0, description="Owner User ID")
    name: str = Field(min_length=2, max_length=120, description="Restaurant name")
    legal_name: Optional[str] = Field(default=None, max_length=150)
    cuisine_type: str = Field(min_length=2, max_length=100)
    gst_no: Optional[str] = Field(
        default=None,
        pattern=r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$",
        description="15-character GSTIN format"
    )
    fssai_no: Optional[str] = Field(
        default=None,
        pattern=r"^[0-9]{14}$",
        description="14-digit FSSAI number"
    )
    contact_email: EmailStr
    contact_phone: str = Field(min_length=8, max_length=20)
    logo_url: Optional[str] = None
    status: Literal["ACTIVE", "INACTIVE", "SUSPENDED"] = "ACTIVE"
    credit_limit: float = Field(default=0, ge=0)
    payment_terms_days: int = Field(default=0, ge=0)


class RestaurantUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
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


class RestaurantResponse(BaseModel):
    id: int
    owner_user_id: int
    name: str
    legal_name: Optional[str] = None
    cuisine_type: Optional[str] = None
    gst_no: Optional[str] = None
    fssai_no: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    logo_url: Optional[str] = None
    status: str
    credit_limit: float
    payment_terms_days: int
    is_deleted: bool

    model_config = {"from_attributes": True}
