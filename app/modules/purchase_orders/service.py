from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from app.modules.purchase_orders.models import (
    GRNItem,
    GRNStatus,
    GoodsReceiptNote,
    POStatus,
    PurchaseOrder,
    PurchaseOrderItem,
    ReceivedStatus,
)
from app.modules.purchase_orders.schemas import (
    GRNCreate,
    POCreate,
    POUpdate,
)


CENT = Decimal("0.01")
ZERO = Decimal("0")
HUNDRED = Decimal("100")


def money(value: Decimal) -> Decimal:
    return Decimal(str(value)).quantize(
        CENT,
        rounding=ROUND_HALF_UP,
    )


def rollback_and_raise(db: Session, error: Exception):
    db.rollback()
    raise error


def get_po_or_404(db: Session, po_id: int) -> PurchaseOrder:
    po = (
        db.query(PurchaseOrder)
        .options(selectinload(PurchaseOrder.items))
        .filter(PurchaseOrder.id == po_id)
        .first()
    )

    if po is None:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found",
        )

    return po


def get_grn_or_404(
    db: Session,
    grn_id: int,
) -> GoodsReceiptNote:
    grn = (
        db.query(GoodsReceiptNote)
        .options(selectinload(GoodsReceiptNote.items))
        .filter(GoodsReceiptNote.id == grn_id)
        .first()
    )

    if grn is None:
        raise HTTPException(
            status_code=404,
            detail="Goods receipt note not found",
        )

    return grn


# Purchase Orders


def create_po(db: Session, data: POCreate):
    try:
        existing = (
            db.query(PurchaseOrder)
            .filter(PurchaseOrder.po_number == data.po_number)
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Purchase order number already exists",
            )

        if data.expected_date < data.order_date:
            raise HTTPException(
                status_code=400,
                detail="Expected date cannot be before order date",
            )

        subtotal = ZERO
        tax_amount = ZERO
        items = []

        for item_data in data.items:
            quantity = Decimal(str(item_data.qty_ordered))
            unit_price = Decimal(str(item_data.unit_price))
            tax_rate = Decimal(str(item_data.tax_rate))

            base_amount = money(quantity * unit_price)
            item_tax = money(base_amount * tax_rate / HUNDRED)
            line_total = money(base_amount + item_tax)

            subtotal += base_amount
            tax_amount += item_tax

            items.append(
                PurchaseOrderItem(
                    product_id=item_data.product_id,
                    qty_ordered=quantity,
                    qty_received=ZERO,
                    unit_price=unit_price,
                    tax_rate=tax_rate,
                    line_total=line_total,
                    received_status=ReceivedStatus.PENDING,
                )
            )

        subtotal = money(subtotal)
        tax_amount = money(tax_amount)
        discount_amount = money(data.discount_amount)

        total_amount = money(
            subtotal + tax_amount - discount_amount
        )

        if total_amount < ZERO:
            raise HTTPException(
                status_code=400,
                detail="Discount cannot exceed subtotal plus tax",
            )

        po = PurchaseOrder(
            po_number=data.po_number,
            restaurant_id=data.restaurant_id,
            supplier_id=data.supplier_id,
            warehouse_id=data.warehouse_id,
            status=POStatus.DRAFT,
            order_date=data.order_date,
            expected_date=data.expected_date,
            subtotal=subtotal,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total_amount=total_amount,
            currency=data.currency,
            payment_terms=data.payment_terms,
            notes=data.notes,
            created_by=data.created_by,
            items=items,
        )

        db.add(po)
        db.commit()
        db.refresh(po)

        return get_po_or_404(db, po.id)

    except Exception:
        db.rollback()
        raise


def list_pos(db: Session):
    return (
        db.query(PurchaseOrder)
        .options(selectinload(PurchaseOrder.items))
        .order_by(PurchaseOrder.id.desc())
        .all()
    )


def get_po(db: Session, po_id: int):
    return get_po_or_404(db, po_id)


def update_po(
    db: Session,
    po_id: int,
    data: POUpdate,
):
    try:
        po = get_po_or_404(db, po_id)

        if po.status != POStatus.DRAFT:
            raise HTTPException(
                status_code=400,
                detail="Only draft purchase orders can be updated",
            )

        updates = data.model_dump(exclude_unset=True)

        if (
            "expected_date" in updates
            and updates["expected_date"] is None
        ):
            updates
