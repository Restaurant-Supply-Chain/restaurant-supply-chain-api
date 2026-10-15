
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.purchase_orders.models import (
    GoodsReceiptNote,
    GRNItem,
    PurchaseOrder,
    PurchaseOrderItem,
)


def confirm_grn(db: Session, grn_id: int):
    try:
        # Find and lock the GRN
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

        if grn.status == "CONFIRMED":
            raise HTTPException(
                status_code=409,
                detail="Goods receipt note is already confirmed",
            )

        if grn.status != "PENDING":
            raise HTTPException(
                status_code=400,
                detail="Only pending GRNs can be confirmed",
            )

        # Find and lock the purchase order
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

        if po.status not in ("APPROVED", "PARTIALLY_RECEIVED"):
            raise HTTPException(
                status_code=400,
                detail="Purchase order is not available for receiving",
            )

        # Get GRN items
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

        # Lock purchase order items
        po_items = (
            db.query(PurchaseOrderItem)
            .filter(PurchaseOrderItem.po_id == po.id)
            .with_for_update()
            .all()
        )

        po_items_by_product = {
            item.product_id: item for item in po_items
        }

        # Validate and combine duplicate products in the GRN
        received_by_product = {}

        for item in grn_items:
            quantity = item.qty_received

            if quantity is None or quantity <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Received quantity must be greater than zero",
                )

            po_item = po_items_by_product.get(item.product_id)

            if po_item is None:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Product {item.product_id} "
                        "is not in the purchase order"
                    ),
                )

            received_by_product[item.product_id] = (
                received_by_product.get(item.product_id, 0) + quantity
            )

        # Check the total received quantity against the ordered quantity
        for product_id, quantity in received_by_product.items():
            po_item = po_items_by_product[product_id]
            already_received = po_item.qty_received or 0

            if already_received + quantity > po_item.qty_ordered:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Received quantity exceeds ordered quantity "
                        f"for product {product_id}"
                    ),
                )

        # Update purchase order item quantities
        for product_id, quantity in received_by_product.items():
            po_item = po_items_by_product[product_id]
            po_item.qty_received = (po_item.qty_received or 0) + quantity

            if po_item.qty_received >= po_item.qty_ordered:
                po_item.received_status = "COMPLETE"
            else:
                po_item.received_status = "PARTIAL"

        # Update the purchase order status
        all_received = all(
            (item.qty_received or 0) >= item.qty_ordered
            for item in po_items
        )

        po.status = (
            "RECEIVED" if all_received else "PARTIALLY_RECEIVED"
        )

        # Mark the GRN as confirmed
        grn.status = "CONFIRMED"

        db.commit()
        db.refresh(grn)

        return grn

    except Exception:
        db.rollback()
        raise
