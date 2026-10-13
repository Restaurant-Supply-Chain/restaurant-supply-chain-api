
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.modules.purchase_orders.models import (
    PurchaseOrder,
    PurchaseOrderItem,
    GoodsReceiptNote,
    GRNItem,
    POStatus,
    ReceivedStatus,
    GRNStatus,
)
from app.modules.purchase_orders.schemas import POCreate, POUpdate, GRNCreate


CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def money(value):
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def commit_changes(db: Session):
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Duplicate reference or invalid database relationship",
        ) from exc


def get_po(db: Session, po_id: int, lock: bool = False):
    stmt = (
        select(PurchaseOrder)
        .where(PurchaseOrder.id == po_id)
        .options(selectinload(PurchaseOrder.items))
    )
    if lock:
        stmt = stmt.with_for_update()

    po = db.scalar(stmt)
    if po is None:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po


def get_grn(db: Session, grn_id: int):
    grn = db.scalar(
        select(GoodsReceiptNote)
        .where(GoodsReceiptNote.id == grn_id)
        .options(selectinload(GoodsReceiptNote.items))
    )
    if grn is None:
        raise HTTPException(status_code=404, detail="GRN not found")
    return grn


def recalculate_po(po):
    subtotal = ZERO
    tax_total = ZERO

    for item in po.items:
        base = money(Decimal(item.qty_ordered) * Decimal(item.unit_price))
        tax = money(base * Decimal(item.tax_rate) / Decimal("100"))
        item.line_total = money(base + tax)
        subtotal += base
        tax_total += tax

    po.subtotal = money(subtotal)
    po.tax_amount = money(tax_total)
    po.discount_amount = money(po.discount_amount or ZERO)

    if po.discount_amount > po.subtotal + po.tax_amount:
        raise HTTPException(
            status_code=400,
            detail="Discount cannot exceed subtotal plus tax",
        )

    po.total_amount = money(
        po.subtotal + po.tax_amount - po.discount_amount
    )


def create_po(db: Session, data: POCreate):
    po = PurchaseOrder(
        po_number=data.po_number,
        restaurant_id=data.restaurant_id,
        supplier_id=data.supplier_id,
        warehouse_id=data.warehouse_id,
        order_date=data.order_date,
        expected_date=data.expected_date,
        discount_amount=data.discount_amount,
        currency=data.currency.upper(),
        payment_terms=data.payment_terms,
        notes=data.notes,
        created_by=data.created_by,
        status=POStatus.DRAFT,
    )

    for item in data.items:
        po.items.append(
            PurchaseOrderItem(
                product_id=item.product_id,
                qty_ordered=item.qty_ordered,
                qty_received=Decimal("0.000"),
                unit_price=item.unit_price,
                tax_rate=item.tax_rate,
                line_total=ZERO,
                received_status=ReceivedStatus.PENDING,
            )
        )

    recalculate_po(po)
    db.add(po)
    commit_changes(db)
    return get_po(db, po.id)


def list_pos(db: Session):
    return db.scalars(
        select(PurchaseOrder)
        .options(selectinload(PurchaseOrder.items))
        .order_by(PurchaseOrder.id.desc())
    ).all()


def update_po(db: Session, po_id: int, data: POUpdate):
    po = get_po(db, po_id)

    if po.status != POStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Only draft purchase orders can be updated",
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(po, field, value)

    if po.expected_date < po.order_date:
        raise HTTPException(
            status_code=400,
            detail="Expected date cannot be before order date",
        )

    recalculate_po(po)
    commit_changes(db)
    return get_po(db, po.id)


def delete_po(db: Session, po_id: int):
    po = get_po(db, po_id)
    if po.status != POStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Only draft purchase orders can be deleted",
        )

    db.delete(po)
    commit_changes(db)
    return {"message": "Purchase order deleted"}


def submit_po(db: Session, po_id: int):
    po = get_po(db, po_id)
    if po.status != POStatus.DRAFT:
        raise HTTPException(status_code=400, detail="PO must be DRAFT")

    po.status = POStatus.SUBMITTED
    commit_changes(db)
    return get_po(db, po.id)


def approve_po(db: Session, po_id: int, approver_id: int):
    po = get_po(db, po_id)
    if po.status != POStatus.SUBMITTED:
        raise HTTPException(
            status_code=400, detail="Only submitted POs can be approved"
        )

    po.status = POStatus.APPROVED
    po.approved_by = approver_id
    commit_changes(db)
    return get_po(db, po.id)


def cancel_po(db: Session, po_id: int):
    po = get_po(db, po_id)
    if po.status not in (
        POStatus.DRAFT,
        POStatus.SUBMITTED,
        POStatus.APPROVED,
    ):
        raise HTTPException(
            status_code=400, detail="This purchase order cannot be cancelled"
        )

    po.status = POStatus.CANCELLED
    commit_changes(db)
    return get_po(db, po.id)


def close_po(db: Session, po_id: int):
    po = get_po(db, po_id)
    if po.status != POStatus.RECEIVED:
        raise HTTPException(
            status_code=400, detail="Only fully received POs can be closed"
        )

    po.status = POStatus.CLOSED
    commit_changes(db)
    return get_po(db, po.id)


def create_grn(db: Session, data: GRNCreate):
    po = get_po(db, data.po_id, lock=True)

    if po.status not in (POStatus.APPROVED, POStatus.PARTIALLY_RECEIVED):
        raise HTTPException(
            status_code=400,
            detail="PO must be APPROVED or PARTIALLY_RECEIVED",
        )

    if data.warehouse_id != po.warehouse_id:
        raise HTTPException(
            status_code=400,
            detail="GRN warehouse must match PO warehouse",
        )

    po_items = {item.id: item for item in po.items}
    seen = set()

    grn = GoodsReceiptNote(
        grn_no=data.grn_no,
        po_id=data.po_id,
        received_by=data.received_by,
        warehouse_id=data.warehouse_id,
        notes=data.notes,
        status=GRNStatus.DRAFT,
    )

    for entry in data.items:
        if entry.po_item_id in seen:
            raise HTTPException(
                status_code=400, detail="Duplicate PO item in GRN"
            )
        seen.add(entry.po_item_id)

        po_item = po_items.get(entry.po_item_id)
        if po_item is None:
            raise HTTPException(
                status_code=400,
                detail="PO item does not belong to this purchase order",
            )

        if entry.product_id != po_item.product_id:
            raise HTTPException(
                status_code=400, detail="GRN product does not match PO item"
            )

        remaining = Decimal(po_item.qty_ordered) - Decimal(po_item.qty_received)
        if entry.qty_received > remaining:
            raise HTTPException(
                status_code=400,
                detail=f"Quantity exceeds remaining amount for PO item {po_item.id}",
            )

        grn.items.append(
            GRNItem(
                po_item_id=entry.po_item_id,
                product_id=entry.product_id,
                qty_received=entry.qty_received,
                batch_no=entry.batch_no,
                expiry_date=entry.expiry_date,
                unit_cost=entry.unit_cost,
                qc_status=entry.qc_status,
            )
        )

    db.add(grn)
    commit_changes(db)
    return get_grn(db, grn.id)


def list_grns(db: Session):
    return db.scalars(
        select(GoodsReceiptNote)
        .options(selectinload(GoodsReceiptNote.items))
        .order_by(GoodsReceiptNote.id.desc())
    ).all()


def update_inventory_for_grn(db: Session, grn: GoodsReceiptNote):
    # INTEGRATION REQUIRED:
    # Call Dev 5's real inventory service here.
    # Use the same DB transaction and define how QC FAIL/PARTIAL stock is handled.
    raise HTTPException(
        status_code=501,
        detail="Dev 5 inventory service must be connected before confirmation",
    )


def confirm_grn(db: Session, grn_id: int):
    grn = get_grn(db, grn_id)

    if grn.status != GRNStatus.DRAFT:
        raise HTTPException(
            status_code=400, detail="Only draft GRNs can be confirmed"
        )

    po = get_po(db, grn.po_id, lock=True)
    if po.status not in (POStatus.APPROVED, POStatus.PARTIALLY_RECEIVED):
        raise HTTPException(
            status_code=400, detail="PO is not available for receiving"
        )

    po_items = {item.id: item for item in po.items}

    # Revalidate quantities at confirmation time.
    for entry in grn.items:
        po_item = po_items.get(entry.po_item_id)
        if po_item is None:
            raise HTTPException(status_code=400, detail="Invalid PO item")

        remaining = Decimal(po_item.qty_ordered) - Decimal(po_item.qty_received)
        if entry.qty_received > remaining:
            raise HTTPException(
                status_code=400,
                detail=f"Quantity exceeds remaining amount for PO item {po_item.id}",
            )

    # This intentionally fails until inventory integration is implemented.
    update_inventory_for_grn(db, grn)

    for entry in grn.items:
        po_item = po_items[entry.po_item_id]
        po_item.qty_received = (
            Decimal(po_item.qty_received) + Decimal(entry.qty_received)
        )
        po_item.received_status = (
            ReceivedStatus.COMPLETE
            if po_item.qty_received == po_item.qty_ordered
            else ReceivedStatus.PARTIAL
        )

    grn.status = GRNStatus.CONFIRMED

    po.status = (
        POStatus.RECEIVED
        if all(item.qty_received == item.qty_ordered for item in po.items)
        else POStatus.PARTIALLY_RECEIVED
    )

    commit_changes(db)
    return get_grn(db, grn.id)


def reject_grn(db: Session, grn_id: int):
    grn = get_grn(db, grn_id)
    if grn.status != GRNStatus.DRAFT:
        raise HTTPException(
            status_code=400, detail="Only draft GRNs can be rejected"
        )

    grn.status = GRNStatus.REJECTED
    commit_changes(db)
    return get_grn(db, grn.id)
