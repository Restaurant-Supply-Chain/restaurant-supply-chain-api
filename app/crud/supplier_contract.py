from sqlalchemy.orm import Session

from app.models.supplier_contract import SupplierContract
from app.schemas.supplier_contract import (
    SupplierContractCreate,
    SupplierContractUpdate,
)


# CREATE: Create a supplier contract
def create_supplier_contract(
    db: Session,
    contract: SupplierContractCreate,
):
    db_contract = SupplierContract(**contract.model_dump())

    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)

    return db_contract


# READ: Get one contract by ID
def get_supplier_contract(db: Session, contract_id: int):
    return (
        db.query(SupplierContract)
        .filter(SupplierContract.id == contract_id)
        .first()
    )


# READ: Get contracts for a supplier
def get_supplier_contracts(
    db: Session,
    supplier_id: int,
    skip: int = 0,
    limit: int = 100,
):
    return (
        db.query(SupplierContract)
        .filter(SupplierContract.supplier_id == supplier_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


# UPDATE: Update a contract
def update_supplier_contract(
    db: Session,
    contract_id: int,
    contract_data: SupplierContractUpdate,
):
    db_contract = get_supplier_contract(db, contract_id)

    if db_contract is None:
        return None

    update_data = contract_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_contract, field, value)

    db.commit()
    db.refresh(db_contract)

    return db_contract


# DELETE: Delete a contract
def delete_supplier_contract(db: Session, contract_id: int):
    db_contract = get_supplier_contract(db, contract_id)

    if db_contract is None:
        return None

    db.delete(db_contract)
    db.commit()

    return db_contract