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


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


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


def get_grn_or_404(db: Session, grn_id: int) -> GoodsReceiptNote:
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
            base_amount = money(
                item_data.qty_ordered * item_data.unit_price
            )
            item_tax = money(
                base_amount * item_data.tax_rate / Decimal("100")
            )
            line_total = base_amount + item_tax

            subtotal += base_amount
            tax_amount += item_tax

            items.append(
                PurchaseOrderItem(
                    product_id=item_data.product_id,
                    qty_ordered=item_data.qty_ordered,
                    qty_received=ZERO,
                    unit_price=item_data.unit_price,
                    tax_rate=item_data.tax_rate,
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


def update_po(db: Session, po_id: int, data: POUpdate):
    try:
        po = get_po_or_404(db, po_id)

        if po.status != POStatus.DRAFT:
            raise HTTPException(
                status_code=400,
                detail="Only draft purchase orders can be updated",
            )

        updates = data.model_dump(exclude_unset=True)

        for field, value in updates.items():
            setattr(po, field, value)

        if po.expected_date < po.order_date:
            raise HTTPException(
                status_code=400,
                detail="Expected date cannot be before order date",
            )

        po.total_amount = money(
            po.subtotal + po.tax_amount - po.discount_amount
        )

        if po.total_amount < ZERO:
            raise HTTPException(
                status_code=400,
                detail="Discount cannot exceed subtotal plus tax",
            )

        db.commit()
        return get_po_or_404(db, po.id)

    except Exception:
        db.rollback()
        raise


def delete_po(db: Session, po_id: int):
    try:
        po = get_po_or_404(db, po_id)

        if po.status != POStatus.DRAFT:
            raise HTTPException(
                status_code=400,
                detail="Only draft purchase orders can be deleted",
            )

        db.delete(po)
        db.commit()

        return {
            "message": "Purchase order deleted successfully",
            "po_id": po_id,
        }

    except Exception:
        db.rollback()
        raise


def submit_po(db: Session, po_id: int):
    try:
        po = get_po_or_404(db, po_id)

        if po.status != POStatus.DRAFT:
            raise HTTPException(
                status_code=400,
                detail="Only draft purchase orders can be submitted",
            )

        if not po.items:
            raise HTTPException(
                status_code=400,
                detail="Purchase order must contain at least one item",
            )

        po.status = POStatus.SUBMITTED
        db.commit()

        return get_po_or_404(db, po.id)

    except Exception:
        db.rollback()
        raise


def approve_po(db: Session, po_id: int, approved_by: int):
    try:
        po = get_po_or_404(db, po_id)

        if po.status != POStatus.SUBMITTED:
            raise HTTPException(
                status_code=400,
                detail="Only submitted purchase orders can be approved",
            )

        if approved_by <= 0:
            raise HTTPException(
                status_code=400,
                detail="Approver ID must be greater than zero",
            )

        po.status = POStatus.APPROVED
        po.approved_by = approved_by

        db.commit()
        return get_po_or_404(db, po.id)

    except Exception:
        db.rollback()
        raise


def cancel_po(db: Session, po_id: int):
    try:
        po = get_po_or_404(db, po_id)

        if po.status not in (
            POStatus.DRAFT,
            POStatus.SUBMITTED,
        ):
            raise HTTPException(
                status_code=400,
                detail="Only draft or submitted purchase orders can be cancelled",
            )

        po.status = POStatus.CANCELLED
        db.commit()

        return get_po_or_404(db, po.id)

    except Exception:
        db.rollback()
        raise


def close_po(db: Session, po_id: int):
    try:
        po = get_po_or_404(db, po_id)

        if po.status != POStatus.RECEIVED:
            raise HTTPException(
                status_code=400,
                detail="Only fully received purchase orders can be closed",
            )

        po.status = POStatus.CLOSED
        db.commit()

        return get_po_or_404(db, po.id)

    except Exception:
        db.rollback()
        raise


# Goods Receipt Notes (GRN)


def create_grn(db: Session, data: GRNCreate):
    try:
        existing = (
            db.query(GoodsReceiptNote)
            .filter(GoodsReceiptNote.grn_no == data.grn_no)
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="GRN number already exists",
            )

        po = get_po_or_404(db, data.po_id)

        if po.status not in (
            POStatus.APPROVED,
            POStatus.PARTIALLY_RECEIVED,
        ):
            raise HTTPException(
                status_code=400,
                detail="Purchase order is not available for receiving",
            )

        if data.warehouse_id != po.warehouse_id:
            raise HTTPException(
                status_code=400,
                detail="GRN warehouse must match the purchase order warehouse",
            )

        po_items = {item.id: item for item in po.items}
        grn_items = []

        for item_data in data.items:
            po_item = po_items.get(item_data.po_item_id)

            if po_item is None:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Purchase order item {item_data.po_item_id} "
                        "does not belong to this purchase order"
                    ),
                )

            if item_data.product_id != po_item.product_id:
                raise HTTPException(
                    status_code=400,
                    detail="GRN product does not match the purchase order item",
                )

            grn_items.append(
                GRNItem(
                    po_item_id=item_data.po_item_id,
                    product_id=item_data.product_id,
                    qty_received=item_data.qty_received,
                    batch_no=item_data.batch_no,
                    expiry_date=item_data.expiry_date,
                    unit_cost=item_data.unit_cost,
                    qc_status=item_data.qc_status,
                )
            )

        grn = GoodsReceiptNote(
            grn_no=data.grn_no,
            po_id=data.po_id,
            received_by=data.received_by,
            warehouse_id=data.warehouse_id,
            notes=data.notes,
            status=GRNStatus.PENDING,
            items=grn_items,
        )

        db.add(grn)
        db.commit()
        db.refresh(grn)

        return get_grn_or_404(db, grn.id)

    except Exception:
        db.rollback()
        raise


def list_grns(db: Session):
    return (
        db.query(GoodsReceiptNote)
        .options(selectinload(GoodsReceiptNote.items))
        .order_by(GoodsReceiptNote.id.desc())
        .all()
    )


def get_grn(db: Session, grn_id: int):
    return get_grn_or_404(db, grn_id)


def confirm_grn(db: Session, grn_id: int):
    try:
        grn = (
            db.query(GoodsReceiptNote)
            .filter(GoodsReceiptNote.id == grn_id)
            .with_for_update()
            .first()
        )

        if grn is None:
            raise HTTPException(
                status_code=404,
                detail="Goods receipt note not found",
            )

        if grn.status != GRNStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail="Only pending GRNs can be confirmed",
            )

        po = (
            db.query(PurchaseOrder)
            .filter(PurchaseOrder.id == grn.po_id)
            .with_for_update()
            .first()
        )

        if po is None:
            raise HTTPException(
                status_code=404,
                detail="Purchase order not found",
            )

        if po.status not in (
            POStatus.APPROVED,
            POStatus.PARTIALLY_RECEIVED,
        ):
            raise HTTPException(
                status_code=400,
                detail="Purchase order is not available for receiving",
            )

        if grn.warehouse_id != po.warehouse_id:
            raise HTTPException(
                status_code=400,
                detail="GRN warehouse does not match the purchase order",
            )

        grn_items = (
            db.query(GRNItem)
            .filter(GRNItem.grn_id == grn.id)
            .all()
        )

        if not grn_items:
            raise HTTPException(
                status_code=400,
                detail="GRN must contain at least one item",
            )

        po_items = (
            db.query(PurchaseOrderItem)
            .filter(PurchaseOrderItem.po_id == po.id)
            .with_for_update()
            .all()
        )

        po_items_by_id = {item.id: item for item in po_items}
        received_by_po_item = {}

        for grn_item in grn_items:
            quantity = grn_item.qty_received

            if quantity is None or quantity <= ZERO:
                raise HTTPException(
                    status_code=400,
                    detail="Received quantity must be greater than zero",
                )

            po_item = po_items_by_id.get(grn_item.po_item_id)

            if po_item is None:
                raise HTTPException(
                    status_code=400,
                    detail="GRN item does not belong to this purchase order",
                )

            if grn_item.product_id != po_item.product_id:
                raise HTTPException(
                    status_code=400,
                    detail="GRN product does not match the purchase order item",
                )

            received_by_po_item[po_item.id] = (
                received_by_po_item.get(po_item.id, ZERO) + quantity
            )

        for item_id, quantity in received_by_po_item.items():
            po_item = po_items_by_id[item_id]
            already_received = po_item.qty_received or ZERO

            if already_received + quantity > po_item.qty_ordered:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Received quantity exceeds ordered quantity "
                        f"for purchase order item {item_id}"
                    ),
                )

        for item_id, quantity in received_by_po_item.items():
            po_item = po_items_by_id[item_id]
            po_item.qty_received = (
                (po_item.qty_received or ZERO) + quantity
            )

            po_item.received_status = (
                ReceivedStatus.COMPLETE
                if po_item.qty_received >= po_item.qty_ordered
                else ReceivedStatus.PARTIAL
            )

        all_received = all(
            (item.qty_received or ZERO) >= item.qty_ordered
            for item in po_items
        )

        po.status = (
            POStatus.RECEIVED
            if all_received
            else POStatus.PARTIALLY_RECEIVED
        )

        grn.status = GRNStatus.CONFIRMED

        db.commit()
        return get_grn_or_404(db, grn.id)

    except Exception:
        db.rollback()
        raise


def reject_grn(db: Session, grn_id: int):
    try:
        grn = get_grn_or_404(db, grn_id)

        if grn.status != GRNStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail="Only pending GRNs can be rejected",
            )

        grn.status = GRNStatus.REJECTED
        db.commit()

        return get_grn_or_404(db, grn.id)

    except Exception:
        db.rollback()
        raise
