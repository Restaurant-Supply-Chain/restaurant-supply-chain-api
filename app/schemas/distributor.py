from pydantic import BaseModel, ConfigDict
from typing import Optional


class DistributorCreate(BaseModel):
    name: str
    region: Optional[str] = None
    contact: Optional[str] = None
    parent_supplier_id: Optional[int] = None


class DistributorUpdate(BaseModel):
    name: Optional[str] = None
    region: Optional[str] = None
    contact: Optional[str] = None
    parent_supplier_id: Optional[int] = None


class DistributorResponse(BaseModel):
    id: int
    name: str
    region: Optional[str] = None
    contact: Optional[str] = None
    parent_supplier_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)