from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
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


# Purchase Orders

@router.post(
    "/purchase-orders",
    response_model=POOut,
    status_code=status.HTTP_201_CREATED,
)
def create_po(
    data: POCreate,
    db: Session = Depends(get_db),
):
    return service.create_po(db, data)


@router.get(
    "/purchase-orders",
    response_model=list[POOut],
)
def list_purchase_orders(
    db: Session = Depends(get_db),
):
    return service.list_pos(db)


@router.get(
    "/purchase-orders/{po_id}",
    response_model=POOut,
)
def get_purchase_order(
    po_id: int,
    db: Session = Depends(get_db),
):
    return service.get_po(db, po_id)


@router.patch(
    "/purchase-orders/{po_id}",
    response_model=POOut,
)
def update_purchase_order(
    po_id: int,
    data: POUpdate,
    db: Session = Depends(get_db),
):
    return service.update_po(db, po_id, data)


@router.delete("/purchase-orders/{po_id}")
def delete_purchase_order(
    po_id: int,
    db: Session = Depends(get_db),
):
    return service.delete_po(db, po_id)


@router.post(
    "/purchase-orders/{po_id}/submit",
    response_model=POOut,
)
def submit_purchase_order(
    po_id: int,
    db: Session = Depends(get_db),
):
    return service.submit_po(db, po_id)


@router.post(
    "/purchase-orders/{po_id}/approve",
    response_model=POOut,
)
def approve_purchase_order(
    po_id: int,
    approved_by: int = Query(
        gt=0,
        description="Temporary development parameter; use the authenticated user in production",
    ),
    db: Session = Depends(get_db),
):
<<<<<<< Updated upstream
    return service.approve
=======
    return service.approve
>>>>>>> Stashed changes
