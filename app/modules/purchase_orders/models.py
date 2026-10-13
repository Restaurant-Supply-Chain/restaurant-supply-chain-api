
from enum import Enum

# IMPORTANT: change this import if your existing shared Base is in another file.
from app.db.base import Base
from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


def enum_values(enum_cls):
    return [member.value for member in enum_cls]


class POStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"
    CLOSED = "CLOSED"


class ReceivedStatus(str, Enum):
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    COMPLETE = "COMPLETE"


class GRNStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"


class QCStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    po_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    restaurant_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("restaurants.id"), nullable=False
    )
    supplier_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("suppliers.id"), nullable=False
    )
    warehouse_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("warehouses.id"), nullable=False
    )
    status: Mapped[POStatus] = mapped_column(
        SAEnum(POStatus, values_callable=enum_values, name="po_status"),
        default=POStatus.DRAFT,
        nullable=False,
    )
    order_date: Mapped[Date] = mapped_column(Date, nullable=False)
    expected_date: Mapped[Date] = mapped_column(Date, nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    payment_terms: Mapped[str | None] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(String(500))
    created_by: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    approved_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )

    items: Mapped[list["PurchaseOrderItem"]] = relationship(
        back_populates="purchase_order", cascade="all, delete-orphan"
    )


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    po_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("purchase_orders.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("products.id"), nullable=False
    )
    qty_ordered: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    qty_received: Mapped[float] = mapped_column(Numeric(14, 3), default=0)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    line_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    received_status: Mapped[ReceivedStatus] = mapped_column(
        SAEnum(
            ReceivedStatus,
            values_callable=enum_values,
            name="received_status",
        ),
        default=ReceivedStatus.PENDING,
        nullable=False,
    )

    purchase_order: Mapped["PurchaseOrder"] = relationship(back_populates="items")


class GoodsReceiptNote(Base):
    __tablename__ = "goods_receipt_notes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    grn_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    po_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("purchase_orders.id"), nullable=False
    )
    received_by: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    received_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    warehouse_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("warehouses.id"), nullable=False
    )
    status: Mapped[GRNStatus] = mapped_column(
        SAEnum(GRNStatus, values_callable=enum_values, name="grn_status"),
        default=GRNStatus.DRAFT,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(String(500))

    items: Mapped[list["GRNItem"]] = relationship(
        back_populates="grn", cascade="all, delete-orphan"
    )


class GRNItem(Base):
    __tablename__ = "grn_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    grn_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("goods_receipt_notes.id"), nullable=False
    )
    po_item_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("purchase_order_items.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("products.id"), nullable=False
    )
    qty_received: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    batch_no: Mapped[str | None] = mapped_column(String(64))
    expiry_date: Mapped[Date | None] = mapped_column(Date)
    unit_cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    qc_status: Mapped[QCStatus] = mapped_column(
        SAEnum(QCStatus, values_callable=enum_values, name="qc_status"),
        default=QCStatus.PASS,
        nullable=False,
    )

    grn: Mapped["GoodsReceiptNote"] = relationship(back_populates="items")
