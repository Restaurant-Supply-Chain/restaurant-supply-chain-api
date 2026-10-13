
# Change this import to the location of your project's existing get_db function.
from app.db.session import get_db
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.modules.purchase_orders import service
from app.modules.purchase_orders.schemas import (
    GRNCreate,
    GRNOut,
    POCreate,
    POOut,
    POUpdate,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["Dev 6 - Purchase Orders and GRN"],
)


@router.post(
    "/purchase-orders",
    response_model=POOut,
    status_code=status.HTTP_201_CREATED,
)
def create_po(data: POCreate, db: Session = Depends(get_db)):
    return service.create_po(db, data)


@router.get("/purchase-orders", response_model=list[POOut])
def list_purchase_orders(db: Session = Depends(get_db)):
    return service.list_pos(db)


@router.get("/purchase-orders/{po_id}", response_model=POOut)
def get_purchase_order(po_id: int, db: Session = Depends(get_db)):
    return service.get_po(db, po_id)


@router.patch("/purchase-orders/{po_id}", response_model=POOut)
def update_purchase_order(
    po_id: int,
    data: POUpdate,
    db: Session = Depends(get_db),
):
    return service.update_po(db, po_id, data)


@router.delete("/purchase-orders/{po_id}")
def delete_purchase_order(po_id: int, db: Session = Depends(get_db)):
    return service.delete_po(db, po_id)


@router.post("/purchase-orders/{po_id}/submit", response_model=POOut)
def submit_purchase_order(po_id: int, db: Session = Depends(get_db)):
    return service.submit_po(db, po_id)


@router.post("/purchase-orders/{po_id}/approve", response_model=POOut)
def approve_purchase_order(
    po_id: int,
    approved_by: int = Query(
        gt=0,
        description="Temporary development parameter; use the authenticated user in production",
    ),
    db: Session = Depends(get_db),
):
    return service.approve_po(db, po_id, approved_by)


@router.post("/purchase-orders/{po_id}/cancel", response_model=POOut)
def cancel_purchase_order(po_id: int, db: Session = Depends(get_db)):
    return service.cancel_po(db, po_id)


@router.post("/purchase-orders/{po_id}/close", response_model=POOut)
def close_purchase_order(po_id: int, db: Session = Depends(get_db)):
    return service.close_po(db, po_id)


@router.post(
    "/grns",
    response_model=GRNOut,
    status_code=status.HTTP_201_CREATED,
)
def create_grn(data: GRNCreate, db: Session = Depends(get_db)):
    return service.create_grn(db, data)


@router.get("/grns", response_model=list[GRNOut])
def list_grns(db: Session = Depends(get_db)):
    return service.list_grns(db)


@router.get("/grns/{grn_id}", response_model=GRNOut)
def get_grn(grn_id: int, db: Session = Depends(get_db)):
    return service.get_grn(db, grn_id)


@router.post("/grns/{grn_id}/confirm", response_model=GRNOut)
def confirm_grn(grn_id: int, db: Session = Depends(get_db)):
    return service.confirm_grn(db, grn_id)


@router.post("/grns/{grn_id}/reject", response_model=GRNOut)
def reject_grn(grn_id: int, db: Session = Depends(get_db)):
    return service.reject_grn(db, grn_id)
