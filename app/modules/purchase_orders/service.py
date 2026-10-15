from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.purchase_orders.models import (
    GoodsReceiptNote,
    GRNItem,
    PurchaseOrder,
    PurchaseOrderItem,
)

def update_inventory(db: Session, warehouse_id: int, product_id: int, quantity):
    """
    Integration point for Dev 5's inventory module.

    Replace this function's body with the actual inventory model
    and stock-update logic used by Dev 5.
    """
    from app.modules.inventory.models import Inventory

    inventory = (
        db.query(Inventory)
        .filter(
            Inventory.warehouse_id == warehouse_id,
            Inventory.product_id == product_id,
        )
        .with_for_update()
        .first()
    )

    if inventory is None:
        inventory = Inventory(
            warehouse_id=warehouse_id,
            product_id=product_id,
            quantity=quantity,
        )
        db.add(inventory)
    else:
        inventory.quantity += quantity

    db.flush()


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
        po_items_by_product = {
            item.product_id: item for item in po_items
        }

        for item in grn_items:
            po_item = po_items_by_product.get(item.product_id)

            if po_item is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product {item.product_id} is not in the purchase order",
                )

            if item.qty_received <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Received quantity must be greater than zero",
                )

            if po_item.qty_received + item.qty_received > po_item.qty_ordered:
                raise HTTPException(
                    status_code=400,
                    detail=f"Received quantity exceeds ordered quantity for product {item.product_id}",
                )

        for item in grn_items:
            po_item = po_items_by_product[item.product_id]
            po_item.qty_received += item.qty_received

            update_inventory(
                db=db,
                warehouse_id=po.warehouse_id,
                product_id=item.product_id,
                quantity=item.qty_received,
            )

            if po_item.qty_received >= po_item.qty_ordered:
                po_item.received_status = "COMPLETE"
            else:
                po_item.received_status = "PARTIAL"

        all_received = all(
            item.qty_received >= item.qty_ordered
            for item in po_items
        )

        po.status = "RECEIVED" if all_received else "PARTIALLY_RECEIVED"
        grn.status = "CONFIRMED"

        db.commit()
        db.refresh(grn)

        return grn

    except Exception:
        db.rollback()
        raise
