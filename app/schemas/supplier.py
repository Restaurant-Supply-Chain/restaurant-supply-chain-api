from pydantic import BaseModel, ConfigDict, EmailStr
from decimal import Decimal
from typing import Optional


class SupplierCreate(BaseModel):
    owner_user_id: int
    business_name: str
    legal_name: Optional[str] = None
    gst_no: Optional[str] = None
    fssai_no: Optional[str] = None
    pan_no: Optional[str] = None
    category: str
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    min_order_value: Decimal = Decimal("0")
    cutoff_time: Optional[str] = None
    delivery_radius_km: Optional[int] = None


class SupplierUpdate(BaseModel):
    business_name: Optional[str] = None
    legal_name: Optional[str] = None
    gst_no: Optional[str] = None
    fssai_no: Optional[str] = None
    pan_no: Optional[str] = None
    category: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    min_order_value: Optional[Decimal] = None
    cutoff_time: Optional[str] = None
    delivery_radius_km: Optional[int] = None
    status: Optional[str] = None


class SupplierResponse(BaseModel):
    id: int
    owner_user_id: int
    business_name: str
    legal_name: Optional[str] = None
    gst_no: Optional[str] = None
    fssai_no: Optional[str] = None
    pan_no: Optional[str] = None
    category: str
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    min_order_value: Decimal
    cutoff_time: Optional[str] = None
    delivery_radius_km: Optional[int] = None
    rating: Decimal
    status: str

    model_config = ConfigDict(from_attributes=True)