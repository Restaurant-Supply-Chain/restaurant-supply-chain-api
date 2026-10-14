from pydantic import BaseModel, ConfigDict
from typing import Optional


class SupplierBankAccountCreate(BaseModel):
    supplier_id: int
    account_holder: str
    account_no: str
    ifsc: str
    bank_name: str
    is_primary: bool = False


class SupplierBankAccountUpdate(BaseModel):
    account_holder: Optional[str] = None
    account_no: Optional[str] = None
    ifsc: Optional[str] = None
    bank_name: Optional[str] = None
    is_primary: Optional[bool] = None


class SupplierBankAccountResponse(BaseModel):
    id: int
    supplier_id: int
    account_holder: str
    account_no: str
    ifsc: str
    bank_name: str
    is_primary: bool

    model_config = ConfigDict(from_attributes=True)