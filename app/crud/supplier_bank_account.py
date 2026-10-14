from sqlalchemy.orm import Session

from app.models.supplier_bank_account import SupplierBankAccount
from app.schemas.supplier_bank_account import (
    SupplierBankAccountCreate,
    SupplierBankAccountUpdate,
)


# CREATE: Add a bank account
def create_bank_account(
    db: Session,
    bank_account: SupplierBankAccountCreate,
):
    db_bank_account = SupplierBankAccount(
        **bank_account.model_dump()
    )

    db.add(db_bank_account)
    db.commit()
    db.refresh(db_bank_account)

    return db_bank_account


# READ: Get one bank account by ID
def get_bank_account(db: Session, account_id: int):
    return (
        db.query(SupplierBankAccount)
        .filter(SupplierBankAccount.id == account_id)
        .first()
    )


# READ: Get bank accounts belonging to a supplier
def get_bank_accounts(
    db: Session,
    supplier_id: int,
    skip: int = 0,
    limit: int = 100,
):
    return (
        db.query(SupplierBankAccount)
        .filter(SupplierBankAccount.supplier_id == supplier_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


# UPDATE: Update a bank account
def update_bank_account(
    db: Session,
    account_id: int,
    account_data: SupplierBankAccountUpdate,
):
    db_bank_account = get_bank_account(db, account_id)

    if db_bank_account is None:
        return None

    update_data = account_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_bank_account, field, value)

    db.commit()
    db.refresh(db_bank_account)

    return db_bank_account


# DELETE: Delete a bank account
def delete_bank_account(db: Session, account_id: int):
    db_bank_account = get_bank_account(db, account_id)

    if db_bank_account is None:
        return None

    db.delete(db_bank_account)
    db.commit()

    return db_bank_account