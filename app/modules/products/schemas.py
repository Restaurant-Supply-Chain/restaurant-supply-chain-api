from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    parent_id: int | None = None


class CategoryOut(ORMBase):
    id: int
    name: str
    description: str | None
    parent_id: int | None
    is_active: bool


class BrandCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class BrandOut(ORMBase):
    id: int
    name: str
    description: str | None
    is_active: bool


class UnitCreate(BaseModel):
    code: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=50)


class UnitOut(ORMBase):
    id: int
    code: str
    name: str
    is_active: bool


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    sku: str = Field(min_length=1, max_length=80)
    description: str | None = None
    supplier_id: int | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, gt=0)
    brand_id: int | None = Field(default=None, gt=0)
    unit_id: int = Field(gt=0)
    base_price: Decimal = Field(default=Decimal("0"), ge=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    category_id: int | None = Field(default=None, gt=0)
    brand_id: int | None = Field(default=None, gt=0)
    unit_id: int | None = Field(default=None, gt=0)
    base_price: Decimal | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductOut(ORMBase):
    id: int
    name: str
    sku: str
    description: str | None
    supplier_id: int | None
    category_id: int | None
    brand_id: int | None
    unit_id: int
    base_price: Decimal
    is_active: bool


class CatalogCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None


class CatalogOut(ORMBase):
    id: int
    name: str
    description: str | None
    is_active: bool


class CatalogItemCreate(BaseModel):
    catalog_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    is_available: bool = True


class CatalogItemOut(ORMBase):
    id: int
    catalog_id: int
    product_id: int
    is_available: bool


class PriceListCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    description: str | None = None


class PriceListOut(ORMBase):
    id: int
    name: str
    currency: str
    description: str | None
    is_active: bool


class PriceListItemCreate(BaseModel):
    price_list_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    price: Decimal = Field(ge=0)


class PriceListItemOut(ORMBase):
    id: int
    price_list_id: int
    product_id: int
    price: Decimal


class StockSettingCreate(BaseModel):
    product_id: int = Field(gt=0)
    minimum_stock: Decimal = Field(default=Decimal("0"), ge=0)
    reorder_quantity: Decimal = Field(default=Decimal("0"), ge=0)
    is_stock_tracked: bool = True


class StockSettingOut(ORMBase):
    id: int
    product_id: int
    minimum_stock: Decimal
    reorder_quantity: Decimal
    is_stock_tracked: bool