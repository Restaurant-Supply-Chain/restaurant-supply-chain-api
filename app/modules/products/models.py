from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    parent: Mapped["Category | None"] = relationship(
        "Category",
        remote_side="Category.id",
        back_populates="children",
    )
    children: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="parent",
    )


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )


class UnitOfMeasure(Base):
    __tablename__ = "units_of_measure"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        UniqueConstraint(
            "supplier_id", "sku", name="uq_product_supplier_sku"
        ),
        CheckConstraint("base_price >= 0", name="ck_product_price"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    sku: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    supplier_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, index=True
    )
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
    brand_id: Mapped[int | None] = mapped_column(
        ForeignKey("brands.id"), nullable=True
    )
    unit_id: Mapped[int] = mapped_column(
        ForeignKey("units_of_measure.id"), nullable=False
    )

    base_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    category: Mapped["Category | None"] = relationship()
    brand: Mapped["Brand | None"] = relationship()
    unit: Mapped["UnitOfMeasure"] = relationship()


class Catalog(Base):
    __tablename__ = "catalogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )


class CatalogItem(Base):
    __tablename__ = "catalog_items"

    __table_args__ = (
        UniqueConstraint(
            "catalog_id", "product_id", name="uq_catalog_product"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    catalog_id: Mapped[int] = mapped_column(
        ForeignKey("catalogs.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    is_available: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )


class PriceList(Base):
    __tablename__ = "price_lists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    currency: Mapped[str] = mapped_column(
        String(3), default="INR", nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )


class PriceListItem(Base):
    __tablename__ = "price_list_items"

    __table_args__ = (
        UniqueConstraint(
            "price_list_id", "product_id", name="uq_price_list_product"
        ),
        CheckConstraint("price >= 0", name="ck_price_list_item_price"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    price_list_id: Mapped[int] = mapped_column(
        ForeignKey("price_lists.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )


class ProductStockSetting(Base):
    __tablename__ = "product_stock_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    minimum_stock: Mapped[Decimal] = mapped_column(
        Numeric(12, 3), default=Decimal("0"), nullable=False
    )
    reorder_quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 3), default=Decimal("0"), nullable=False
    )
    is_stock_tracked: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )