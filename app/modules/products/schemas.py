
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ============================================================
# BASE ORM SCHEMA
# ============================================================

class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# CATEGORY SCHEMAS
# ============================================================

class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=140)
    parent_id: int | None = Field(default=None, gt=0)
    is_active: bool = True


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    slug: str | None = Field(default=None, min_length=1, max_length=140)
    parent_id: int | None = Field(default=None, gt=0)
    is_active: bool | None = None


class CategoryOut(ORMModel):
    id: int
    name: str
    slug: str
    parent_id: int | None
    is_active: bool


# ============================================================
# BRAND SCHEMAS
# ============================================================

class BrandCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    is_active: bool = True


class BrandUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    is_active: bool | None = None


class BrandOut(ORMModel):
    id: int
    name: str
    description: str | None
    is_active: bool


# ============================================================
# UNIT OF MEASURE SCHEMAS
# ============================================================

class UnitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    code: str = Field(min_length=1, max_length=20)
    is_active: bool = True


class UnitUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    code: str | None = Field(default=None, min_length=1, max_length=20)
    is_active: bool | None = None


class UnitOut(ORMModel):
    id: int
    name: str
    code: str
    is_active: bool


# ============================================================
# PRODUCT SCHEMAS
# ============================================================

class ProductCreate(BaseModel):
    supplier_id: int = Field(gt=0)
    category_id: int = Field(gt=0)
    brand_id: int | None = Field(default=None, gt=0)
    uom_id: int = Field(gt=0)

    sku: str = Field(min_length=1, max_length=80)
    barcode: str | None = Field(default=None, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None

    pack_size: Decimal = Field(default=Decimal("1"), gt=0)
    hsn_code: str | None = Field(default=None, max_length=20)
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    image_url: str | None = Field(default=None, max_length=500)

    is_active: bool = True
    is_perishable: bool = False
    shelf_life_days: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_shelf_life(self):
        if self.is_perishable and self.shelf_life_days is None:
            raise ValueError(
                "shelf_life_days is required for perishable products"
            )
        return self


class ProductUpdate(BaseModel):
    supplier_id: int | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, gt=0)
    brand_id: int | None = Field(default=None, gt=0)
    uom_id: int | None = Field(default=None, gt=0)

    sku: str | None = Field(default=None, min_length=1, max_length=80)
    barcode: str | None = Field(default=None, max_length=100)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None

    pack_size: Decimal | None = Field(default=None, gt=0)
    hsn_code: str | None = Field(default=None, max_length=20)
    tax_rate: Decimal | None = Field(default=None, ge=0, le=100)
    image_url: str | None = Field(default=None, max_length=500)

    is_active: bool | None = None
    is_perishable: bool | None = None
    shelf_life_days: int | None = Field(default=None, ge=0)


class ProductOut(ORMModel):
    id: int
    supplier_id: int
    category_id: int
    brand_id: int | None
    uom_id: int

    sku: str
    barcode: str | None
    name: str
    description: str | None

    pack_size: Decimal
    hsn_code: str | None
    tax_rate: Decimal
    image_url: str | None

    is_active: bool
    is_perishable: bool
    shelf_life_days: int | None


# ============================================================
# CATALOG SCHEMAS
# ============================================================

class CatalogCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    is_active: bool = True


class CatalogOut(ORMModel):
    id: int
    name: str
    description: str | None
    is_active: bool


# ============================================================
# CATALOG ITEM SCHEMAS
# ============================================================

class CatalogItemCreate(BaseModel):
    catalog_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    is_active: bool = True


class CatalogItemOut(ORMModel):
    id: int
    catalog_id: int
    product_id: int
    is_active: bool


# ============================================================
# PRICE LIST SCHEMAS
# ============================================================

class PriceListCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    supplier_id: int = Field(gt=0)
    valid_from: date
    valid_to: date | None = None
    currency: str = Field(default="INR", min_length=3, max_length=3)
    is_active: bool = True

    @model_validator(mode="after")
    def validate_dates(self):
        if self.valid_to is not None and self.valid_to < self.valid_from:
            raise ValueError("valid_to cannot be before valid_from")
        return self


class PriceListOut(ORMModel):
    id: int
    name: str
    supplier_id: int
    valid_from: date
    valid_to: date | None
    currency: str
    is_active: bool


# ============================================================
# PRICE LIST ITEM SCHEMAS
# ============================================================

class PriceItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    min_quantity: Decimal = Field(default=Decimal("1"), gt=0)
    discount_percent: Decimal = Field(
        default=Decimal("0"), ge=0, le=100
    )


class PriceItemOut(ORMModel):
    id: int
    price_list_id: int
    product_id: int
    unit_price: Decimal
    min_quantity: Decimal
    discount_percent: Decimal


# Compatibility aliases for routers using the longer names.
PriceListItemCreate = PriceItemCreate
PriceListItemOut = PriceItemOut


# ============================================================
# PRODUCT STOCK SETTING SCHEMAS
# ============================================================

class StockSettingCreate(BaseModel):
    reorder_point: Decimal = Field(default=Decimal("0"), ge=0)
    safety_stock: Decimal = Field(default=Decimal("0"), ge=0)
    lead_time_days: int = Field(default=0, ge=0)


class StockSettingUpdate(BaseModel):
    reorder_point: Decimal | None = Field(default=None, ge=0)
    safety_stock: Decimal | None = Field(default=None, ge=0)
    lead_time_days: int | None = Field(default=None, ge=0)


class StockSettingOut(ORMModel):
    id: int
    product_id: int
    reorder_point: Decimal
    safety_stock: Decimal
    lead_time_days: int
