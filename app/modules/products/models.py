from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base


class TimestampMixin:
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Category(TimestampMixin, Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    parent = relationship(
        "Category", remote_side="Category.id", back_populates="children"
    )
    children = relationship("Category", back_populates="parent")
    products = relationship("Product", back_populates="category")


class Brand(TimestampMixin, Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    products = relationship("Product", back_populates="brand")


class UnitOfMeasure(TimestampMixin, Base):
    __tablename__ = "units_of_measure"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    products = relationship("Product", back_populates="unit")


class Product(TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("supplier_id", "sku", name="uq_product_supplier_sku"),
        CheckConstraint("tax_rate >= 0 AND tax_rate <= 100", name="ck_product_tax"),
        CheckConstraint("pack_size > 0", name="ck_product_pack_size"),
        CheckConstraint(
            "shelf_life_days IS NULL OR shelf_life_days >= 0",
            name="ck_product_shelf_life",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False, index=True
    )
    brand_id: Mapped[int | None] = mapped_column(
        ForeignKey("brands.id"), nullable=True
    )
    uom_id: Mapped[int] = mapped_column(
        ForeignKey("units_of_measure.id"), nullable=False
    )

    sku: Mapped[str] = mapped_column(String(80), nullable=False)
    barcode: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    pack_size: Mapped[float] = mapped_column(Numeric(12, 3), default=1)
    hsn_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_perishable: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    shelf_life_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    unit = relationship("UnitOfMeasure", back_populates="products")
    price_items = relationship("PriceListItem", back_populates="product")
    stock_setting = relationship(
        "ProductStockSetting", back_populates="product", uselist=False
    )


class PriceList(TimestampMixin, Base):
    __tablename__ = "price_lists"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    valid_from: Mapped[object] = mapped_column(Date, nullable=False)
    valid_to: Mapped[object | None] = mapped_column(Date, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    items = relationship(
        "PriceListItem", back_populates="price_list", cascade="all, delete-orphan"
    )


class PriceListItem(TimestampMixin, Base):
    __tablename__ = "price_list_items"
    __table_args__ = (
        UniqueConstraint("price_list_id", "product_id", name="uq_price_product"),
        CheckConstraint("unit_price >= 0", name="ck_price_nonnegative"),
        CheckConstraint("min_quantity > 0", name="ck_min_quantity"),
        CheckConstraint(
            "discount_percent >= 0 AND discount_percent <= 100",
            name="ck_discount_percent",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    price_list_id: Mapped[int] = mapped_column(
        ForeignKey("price_lists.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), nullable=False
    )
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    min_quantity: Mapped[float] = mapped_column(
        Numeric(12, 3), default=1, nullable=False
    )
    discount_percent: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )

    price_list = relationship("PriceList", back_populates="items")
    product = relationship("Product", back_populates="price_items")


class ProductStockSetting(TimestampMixin, Base):
    __tablename__ = "product_stock_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    reorder_point: Mapped[float] = mapped_column(Numeric(12, 3), default=0)
    safety_stock: Mapped[float] = mapped_column(Numeric(12, 3), default=0)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=0)

    product = relationship("Product", back_populates="stock_setting")
    
class Catalog(TimestampMixin, Base):
    __tablename__ = "catalogs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    items = relationship(
        "CatalogItem",
        back_populates="catalog",
        cascade="all, delete-orphan",
    )


class CatalogItem(TimestampMixin, Base):
    __tablename__ = "catalog_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    catalog_id: Mapped[int] = mapped_column(
        ForeignKey("catalogs.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    catalog = relationship("Catalog", back_populates="items")
    product = relationship("Product")

