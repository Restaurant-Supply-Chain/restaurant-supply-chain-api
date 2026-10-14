from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.crud import supplier as supplier_crud
from app.schemas.supplier import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
)

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.post(
    "/",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_supplier(
    supplier: SupplierCreate,
    db: Session = Depends(get_db),
):
    return supplier_crud.create_supplier(db, supplier)


@router.get("/", response_model=list[SupplierResponse])
def read_suppliers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return supplier_crud.get_suppliers(db, skip=skip, limit=limit)


@router.get("/{supplier_id}", response_model=SupplierResponse)
def read_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
):
    supplier = supplier_crud.get_supplier(db, supplier_id)

    if supplier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )

    return supplier


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db),
):
    supplier = supplier_crud.update_supplier(
        db, supplier_id, supplier_data
    )

    if supplier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )

    return supplier


@router.delete(
    "/{supplier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
):
    supplier = supplier_crud.delete_supplier(db, supplier_id)

    if supplier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )