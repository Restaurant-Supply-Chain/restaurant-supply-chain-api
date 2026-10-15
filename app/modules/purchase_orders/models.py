
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class POStatus(str, PyEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"
    CLOSED = "CLOSED"


class ReceivedStatus(str, PyEnum):
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    COMPLETE = "COMPLETE"


class GRNStatus(str, PyEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"


class QCStatus(str, PyEnum):
    PENDING = "PENDING"
    PASS = "PASS"
    FAIL = "FAIL"


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    po_number: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False
    )

    restaurant_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False
    )
    supplier_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False
    )
    warehouse_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False
    )

    status: Mapped[POStatus] = mapped_column(
        Enum(POStatus, name="po_status"), nullable=False,
        default=POStatus.DRAFT
    )

    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_date: Mapped[date] = mapped_column(Date, nullable=False)

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0")
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0")
    )
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0")
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0")
    )

    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="INR"
    )
    payment_terms: Mapped[str | None] = mapped_column(
        String(40), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    created_by: Mapped[int] = mapped_column(
        BigInteger, nullable=False
    )
    approved_by: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True
    )

    items: Mapped[list["PurchaseOrderItem"]] = relationship(
        back_populates="purchase_order",
        cascade="all, delete-orphan",
    )

    grns: Mapped[list["GoodsReceiptNote"]] = relationship(
        back_populates="purchase_order"
    )


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    po_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("purchase_orders.id"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False
    )

    qty_ordered: Mapped[Decimal] = mapped_column(
        Numeric(14, 3), nullable=False
    )
    qty_received: Mapped[Decimal] = mapped_column(
        Numeric(14, 3), nullable=False, default=Decimal("0")
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )
    tax_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("0")
    )
    line_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False
    )

    received_status: Mapped[ReceivedStatus] = mapped_column(
        Enum(ReceivedStatus, name="received_status"),
        nullable=False,
        default=ReceivedStatus.PENDING,
    )

    purchase_order: Mapped["PurchaseOrder"] = relationship(
        back_populates="items"
    )
    grn_items: Mapped[list["GRNItem"]] = relationship(
        back_populates="purchase_order_item"
    )


class GoodsReceiptNote(Base):
    __tablename__ = "goods_receipt_notes"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    grn_no: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False
    )
    po_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("purchase_orders.id"),
        nullable=False,
    )
    received_by: Mapped[int] = mapped_column(
        BigInteger, nullable=False
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    warehouse_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False
    )
    status: Mapped[GRNStatus] = mapped_column(
        Enum(GRNStatus, name="grn_status"),
        nullable=False,
        default=GRNStatus.PENDING,
    )
    notes: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    purchase_order: Mapped["PurchaseOrder"] = relationship(
        back_populates="grns"
    )
    items: Mapped[list["GRNItem"]] = relationship(
        back_populates="grn",
        cascade="all, delete-orphan",
    )


class GRNItem(Base):
    __tablename__ = "grn_items"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    grn_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("goods_receipt_notes.id"),
        nullable=False,
    )
    po_item_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("purchase_order_items.id"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False
    )

    qty_received: Mapped[Decimal] = mapped_column(
        Numeric(14, 3), nullable=False
    )
    batch_no: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    expiry_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    unit_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )
    qc_status: Mapped[QCStatus] = mapped_column(
        Enum(QCStatus, name="qc_status"),
        nullable=False,
        default=QCStatus.PASS,
    )

    grn: Mapped["GoodsReceiptNote"] = relationship(
        back_populates="items"
    )
    purchase_order_item: Mapped["PurchaseOrderItem"] = relationship(
        back_populates="grn_items"
    )
