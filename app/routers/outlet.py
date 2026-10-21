from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.schemas.outlet import OutletCreate, OutletUpdate, OutletResponse

router = APIRouter(prefix="/outlets", tags=["Outlets"])


@router.post("/", response_model=OutletResponse, status_code=status.HTTP_201_CREATED)
def create_outlet(data: OutletCreate, db: Session = Depends(get_db)):
    """
    Create a new outlet for a restaurant.
    Maintains single default outlet constraint per restaurant.
    """
    # 1. Verify parent restaurant exists and is not soft-deleted
    restaurant = db.query(models.Restaurant).filter(
        models.Restaurant.id == data.restaurant_id,
        models.Restaurant.is_deleted == False
    ).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurant with ID {data.restaurant_id} not found"
        )

    # 2. Check if outlet_code is unique
    existing_code = db.query(models.Outlet).filter(
        models.Outlet.outlet_code == data.outlet_code
    ).first()
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Outlet code '{data.outlet_code}' already exists"
        )

    values = data.model_dump()
    existing_outlets = db.query(models.Outlet).filter(
        models.Outlet.restaurant_id == data.restaurant_id
    ).all()

    # First outlet for a restaurant is always the default
    if not existing_outlets:
        values["is_default"] = True

    # Only one default outlet per restaurant
    if values["is_default"]:
        for outlet in existing_outlets:
            outlet.is_default = False

    new_outlet = models.Outlet(**values)
    db.add(new_outlet)
    db.commit()
    db.refresh(new_outlet)
    return new_outlet


@router.get("/", response_model=List[OutletResponse])
def get_outlets(
    restaurant_id: Optional[int] = Query(None, description="Filter outlets by restaurant ID"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all outlets, optionally filtered by restaurant ID.
    """
    query = db.query(models.Outlet)
    if restaurant_id is not None:
        query = query.filter(models.Outlet.restaurant_id == restaurant_id)
    return query.all()


@router.get("/{outlet_id}", response_model=OutletResponse)
def get_outlet(outlet_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single outlet by ID.
    """
    outlet = db.get(models.Outlet, outlet_id)
    if not outlet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outlet not found"
        )
    return outlet


@router.put("/{outlet_id}", response_model=OutletResponse)
def update_outlet(outlet_id: int, data: OutletUpdate, db: Session = Depends(get_db)):
    """
    Update an outlet.
    """
    outlet = db.get(models.Outlet, outlet_id)
    if not outlet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outlet not found"
        )

    values = data.model_dump(exclude_unset=True)

    # Check outlet_code uniqueness if updated
    if "outlet_code" in values and values["outlet_code"] != outlet.outlet_code:
        existing = db.query(models.Outlet).filter(
            models.Outlet.outlet_code == values["outlet_code"],
            models.Outlet.id != outlet_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Outlet code '{values['outlet_code']}' already exists"
            )

    # If setting this outlet as default, reset other outlets of the same restaurant
    if values.get("is_default") is True:
        db.query(models.Outlet).filter(
            models.Outlet.restaurant_id == outlet.restaurant_id,
            models.Outlet.id != outlet_id
        ).update({"is_default": False})

    for key, value in values.items():
        setattr(outlet, key, value)

    db.commit()
    db.refresh(outlet)
    return outlet


@router.delete("/{outlet_id}")
def delete_outlet(outlet_id: int, db: Session = Depends(get_db)):
    """
    Delete an outlet.
    If the deleted outlet was the default, automatically assign another outlet as default.
    """
    outlet = db.get(models.Outlet, outlet_id)
    if not outlet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outlet not found"
        )

    was_default = outlet.is_default
    restaurant_id = outlet.restaurant_id

    db.delete(outlet)
    db.flush()

    # Reassign default outlet if the default one was deleted
    if was_default:
        next_outlet = db.query(models.Outlet).filter(
            models.Outlet.restaurant_id == restaurant_id
        ).first()
        if next_outlet:
            next_outlet.is_default = True

    db.commit()
    return {"message": "Outlet deleted successfully"}
