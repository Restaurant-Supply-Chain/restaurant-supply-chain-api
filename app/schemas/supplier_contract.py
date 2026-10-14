from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date
from decimal import Decimal


class SupplierContractCreate(BaseModel):
    supplier_id: int
    restaurant_id: int
    contract_no: str
    start_date: date
    end_date: date
    payment_terms: Optional[str] = None
    discount_pct: Decimal = Decimal("0")
    status: str = "DRAFT"


class SupplierContractUpdate(BaseModel):
    contract_no: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    payment_terms: Optional[str] = None
    discount_pct: Optional[Decimal] = None
    status: Optional[str] = None


class SupplierContractResponse(BaseModel):
    id: int
    supplier_id: int
    restaurant_id: int
    contract_no: str
    start_date: date
    end_date: date
    payment_terms: Optional[str] = None
    discount_pct: Decimal
    status: str

    model_config = ConfigDict(from_attributes=True)