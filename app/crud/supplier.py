from sqlalchemy.orm import Session

from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate


# CREATE: Add a new supplier
def create_supplier(db: Session, supplier: SupplierCreate):
    db_supplier = Supplier(**supplier.model_dump())

    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)

    return db_supplier


# READ: Get one supplier by ID
def get_supplier(db: Session, supplier_id: int):
    return (
        db.query(Supplier)
        .filter(Supplier.id == supplier_id)
        .first()
    )


# READ: Get all suppliers
def get_suppliers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Supplier).offset(skip).limit(limit).all()


# UPDATE: Update an existing supplier
def update_supplier(
    db: Session,
    supplier_id: int,
    supplier_data: SupplierUpdate,
):
    db_supplier = get_supplier(db, supplier_id)

    if db_supplier is None:
        return None

    update_data = supplier_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_supplier, field, value)

    db.commit()
    db.refresh(db_supplier)

    return db_supplier


# DELETE: Delete a supplier
def delete_supplier(db: Session, supplier_id: int):
    db_supplier = get_supplier(db, supplier_id)

    if db_supplier is None:
        return None

    db.delete(db_supplier)
    db.commit()

    return db_supplier