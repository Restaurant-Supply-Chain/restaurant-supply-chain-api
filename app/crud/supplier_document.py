from sqlalchemy.orm import Session

from app.models.supplier_document import SupplierDocument
from app.schemas.supplier_document import (
    SupplierDocumentCreate,
    SupplierDocumentUpdate,
)


# CREATE: Register a supplier document
def create_supplier_document(
    db: Session,
    document: SupplierDocumentCreate,
):
    db_document = SupplierDocument(**document.model_dump())

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return db_document


# READ: Get one document by ID
def get_supplier_document(db: Session, document_id: int):
    return (
        db.query(SupplierDocument)
        .filter(SupplierDocument.id == document_id)
        .first()
    )


# READ: Get all documents belonging to a supplier
def get_supplier_documents(
    db: Session,
    supplier_id: int,
    skip: int = 0,
    limit: int = 100,
):
    return (
        db.query(SupplierDocument)
        .filter(SupplierDocument.supplier_id == supplier_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


# UPDATE: Update document details
def update_supplier_document(
    db: Session,
    document_id: int,
    document_data: SupplierDocumentUpdate,
):
    db_document = get_supplier_document(db, document_id)

    if db_document is None:
        return None

    update_data = document_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_document, field, value)

    db.commit()
    db.refresh(db_document)

    return db_document


# DELETE: Delete a document record
def delete_supplier_document(db: Session, document_id: int):
    db_document = get_supplier_document(db, document_id)

    if db_document is None:
        return None

    db.delete(db_document)
    db.commit()

    return db_document