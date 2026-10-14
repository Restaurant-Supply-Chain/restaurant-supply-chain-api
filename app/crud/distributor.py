from sqlalchemy.orm import Session

from app.models.distributor import Distributor
from app.schemas.distributor import DistributorCreate, DistributorUpdate


# CREATE: Add a new distributor
def create_distributor(db: Session, distributor: DistributorCreate):
    db_distributor = Distributor(**distributor.model_dump())

    db.add(db_distributor)
    db.commit()
    db.refresh(db_distributor)

    return db_distributor


# READ: Get one distributor by ID
def get_distributor(db: Session, distributor_id: int):
    return (
        db.query(Distributor)
        .filter(Distributor.id == distributor_id)
        .first()
    )


# READ: Get all distributors
def get_distributors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Distributor).offset(skip).limit(limit).all()


# UPDATE: Update an existing distributor
def update_distributor(
    db: Session,
    distributor_id: int,
    distributor_data: DistributorUpdate,
):
    db_distributor = get_distributor(db, distributor_id)

    if db_distributor is None:
        return None

    update_data = distributor_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_distributor, field, value)

    db.commit()
    db.refresh(db_distributor)

    return db_distributor


# DELETE: Delete a distributor
def delete_distributor(db: Session, distributor_id: int):
    db_distributor = get_distributor(db, distributor_id)

    if db_distributor is None:
        return None

    db.delete(db_distributor)
    db.commit()

    return db_distributor