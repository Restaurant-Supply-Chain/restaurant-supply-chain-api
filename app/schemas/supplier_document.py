from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class SupplierDocumentCreate(BaseModel):
    supplier_id: int
    doc_type: str
    file_url: str
    verified: bool = False
    verified_by: Optional[int] = None
    expires_at: Optional[datetime] = None


class SupplierDocumentUpdate(BaseModel):
    doc_type: Optional[str] = None
    file_url: Optional[str] = None
    verified: Optional[bool] = None
    verified_by: Optional[int] = None
    expires_at: Optional[datetime] = None


class SupplierDocumentResponse(BaseModel):
    id: int
    supplier_id: int
    doc_type: str
    file_url: str
    verified: bool
    verified_by: Optional[int] = None
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)