
from datetime import date, datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.modules.purchase_orders.models import (
    POStatus,
    ReceivedStatus,
    GRNStatus,
    QCStatus,
)


# Purchase order item schemas

class POItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    qty_ordered: Decimal = Field(
        gt=0, max_digits=14, decimal_places=3
    )
    unit_price: Decimal = Field(
        ge=0, max_digits=12, decimal_places=2
    )
    tax_rate: Decimal = Field(
        default=Decimal("0"), ge=0, le=100,
        max_digits=5, decimal_places=2
    )


class POCreate(BaseModel):
    po_number: str = Field(min_length=1, max_length=32)
    restaurant_id: int = Field(gt=0)
    supplier_id: int = Field(gt=0)
    warehouse_id: int = Field(gt=0)
    order_date: date
    expected_date: date
    discount_amount: Decimal = Field(
        default=Decimal("0"), ge=0
    )
    currency: str = Field(default="INR", min_length=3, max_length=3)
    payment_terms: str | None = Field(default=None, max_length=40)
    notes: str | None = Field(default=None, max_length=500)
    created_by: int = Field(gt=0)
    items: list[POItemCreate] = Field(min_length=1)

    @field_validator("po_number")
    @classmethod
    def validate_po_number(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("PO number cannot be empty")
        return value

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        value = value.strip().upper()
        if len(value) != 3 or not value.isalpha():
            raise ValueError("Currency must be a three-letter code")
        return value

    @model_validator(mode="after")
    def check_dates(self):
        if self.expected_date < self.order_date:
            raise ValueError(
                "Expected date cannot be before order date"
            )
        return self


class POUpdate(BaseModel):
    expected_date: date | None = None
    discount_amount: Decimal | None = Field(default=None, ge=0)
    currency: str | None = Field(
        default=None, min_length=3, max_length=3
    )
    payment_terms: str | None = Field(default=None, max_length=40)
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip().upper()
        if len(value) != 3 or not value.isalpha():
            raise ValueError("Currency must be a three-letter code")
        return value


class POItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    po_id: int
    product_id: int
    qty_ordered: Decimal
    qty_received: Decimal
    unit_price: Decimal
    tax_rate: Decimal
    line_total: Decimal
    received_status: ReceivedStatus


class POOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    po_number: str
    restaurant_id: int
    supplier_id: int
    warehouse_id: int
    status: POStatus
    order_date: date
    expected_date: date
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    currency: str
    payment_terms: str | None
    notes: str | None
    created_by: int
    approved_by: int | None
    items: list[POItemOut]


# GRN item schemas

class GRNItemCreate(BaseModel):
    po_item_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    qty_received: Decimal = Field(
        gt=0, max_digits=14, decimal_places=3
    )
    batch_no: str | None = Field(default=None, max_length=64)
    expiry_date: date | None = None
    unit_cost: Decimal = Field(
        ge=0, max_digits=12, decimal_places=2
    )
    qc_status: QCStatus = QCStatus.PASS

    @field_validator("batch_no")
    @classmethod
    def validate_batch_no(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()
            if not value:
                return None
        return value

    @model_validator(mode="after")
    def check_expiry(self):
        if self.expiry_date and self.expiry_date < date.today():
            raise ValueError("Expiry date cannot be in the past")
        return self


class GRNCreate(BaseModel):
    grn_no: str = Field(min_length=1, max_length=32)
    po_id: int = Field(gt=0)
    received_by: int = Field(gt=0)
    warehouse_id: int = Field(gt=0)
    notes: str | None = Field(default=None, max_length=500)
    items: list[GRNItemCreate] = Field(min_length=1)

    @field_validator("grn_no")
    @classmethod
    def validate_grn_no(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("GRN number cannot be empty")
        return value


class GRNItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    grn_id: int
    po_item_id: int
    product_id: int
    qty_received: Decimal
    batch_no: str | None
    expiry_date: date | None
    unit_cost: Decimal
    qc_status: QCStatus


class GRNOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    grn_no: str
    po_id: int
    received_by: int
    received_at: datetime
    warehouse_id: int
    status: GRNStatus
    notes: str | None
    items: list[GRNItemOut]
