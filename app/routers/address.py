from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse

router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.post("/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_address(data: AddressCreate, db: Session = Depends(get_db)):
    """
    Create a new address.
    Optionally marks as default address for the given owner entity.
    """
    values = data.model_dump()

    # If new address is marked as default, reset existing defaults for this owner
    if values.get("is_default") is True:
        db.query(models.Address).filter(
            models.Address.owner_type == values["owner_type"],
            models.Address.owner_id == values["owner_id"]
        ).update({"is_default": False})

    address = models.Address(**values)
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


@router.get("/", response_model=List[AddressResponse])
def get_addresses(
    owner_type: Optional[str] = Query(None, description="Filter by owner type e.g. RESTAURANT, OUTLET, USER"),
    owner_id: Optional[int] = Query(None, description="Filter by owner ID"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all addresses, optionally filtered by owner_type and owner_id.
    """
    query = db.query(models.Address)
    if owner_type:
        query = query.filter(models.Address.owner_type == owner_type)
    if owner_id:
        query = query.filter(models.Address.owner_id == owner_id)
    return query.all()


@router.get("/{address_id}", response_model=AddressResponse)
def get_address(address_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific address by ID.
    """
    address = db.get(models.Address, address_id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    return address


@router.put("/{address_id}", response_model=AddressResponse)
def update_address(address_id: int, data: AddressUpdate, db: Session = Depends(get_db)):
    """
    Update address details.
    """
    address = db.get(models.Address, address_id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )

    values = data.model_dump(exclude_unset=True)

    # If setting this address as default, unset other defaults for this owner
    if values.get("is_default") is True:
        db.query(models.Address).filter(
            models.Address.owner_type == address.owner_type,
            models.Address.owner_id == address.owner_id,
            models.Address.id != address_id
        ).update({"is_default": False})

    for key, value in values.items():
        setattr(address, key, value)

    db.commit()
    db.refresh(address)
    return address


@router.delete("/{address_id}")
def delete_address(address_id: int, db: Session = Depends(get_db)):
    """
    Delete an address by ID.
    """
    address = db.get(models.Address, address_id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )

    db.delete(address)
    db.commit()
    return {"message": "Address deleted successfully"}
