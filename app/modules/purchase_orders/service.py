
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.purchase_orders.models import (
    GRNItem,
    GRNStatus,
    GoodsReceiptNote,
    POStatus,
    PurchaseOrder,
    PurchaseOrderItem,
    ReceivedStatus,
)


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

        if grn.status == GRNStatus.CONFIRMED:
            raise HTTPException(
                status_code=409,
                detail="Goods receipt note is already confirmed",
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

        if not po_items:
            raise HTTPException(
                status_code=400,
                detail="Purchase order has no items",
            )

        po_items_by_id = {item.id: item for item in po_items}

        # Validate all GRN lines before changing any quantities.
        received_by_po_item = {}

        for grn_item in grn_items:
            quantity = grn_item.qty_received

            if quantity is None or quantity <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Received quantity must be greater than zero",
                )

            po_item = po_items_by_id.get(grn_item.po_item_id)

            if po_item is None:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Purchase order item {grn_item.po_item_id} "
                        "does not belong to this purchase order"
                    ),
                )

            if grn_item.product_id != po_item.product_id:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Product ID does not match purchase order item "
                        f"{grn_item.po_item_id}"
                    ),
                )

            received_by_po_item[po_item.id] = (
                received_by_po_item.get(
                    po_item.id, Decimal("0")
                )
                + quantity
            )

        for po_item_id, quantity in received_by_po_item.items():
            po_item = po_items_by_id[po_item_id]
            already_received = po_item.qty_received or Decimal("0")

            if already_received + quantity > po_item.qty_ordered:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Received quantity exceeds ordered quantity "
                        f"for purchase order item {po_item_id}"
                    ),
                )

        # Apply quantities only after all lines pass validation.
        for po_item_id, quantity in received_by_po_item.items():
            po_item = po_items_by_id[po_item_id]
            po_item.qty_received = (
                (po_item.qty_received or Decimal("0")) + quantity
            )

            if po_item.qty_received >= po_item.qty_ordered:
                po_item.received_status = ReceivedStatus.COMPLETE
            else:
                po_item.received_status = ReceivedStatus.PARTIAL

        all_received = all(
            (item.qty_received or Decimal("0")) >= item.qty_ordered
            for item in po_items
        )

        po.status = (
            POStatus.RECEIVED
            if all_received
            else POStatus.PARTIALLY_RECEIVED
        )

        grn.status = GRNStatus.CONFIRMED

        db.commit()
        db.refresh(grn)

        return grn

    except Exception:
        db.rollback()
        raise
