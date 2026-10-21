import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate, RestaurantResponse

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.post("/", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
def create_restaurant(data: RestaurantCreate, db: Session = Depends(get_db)):
    """
    Create a new restaurant.
    Automatically creates a default outlet for the restaurant upon creation.
    """
    # 1. Verify owner user exists
    owner = db.get(models.User, data.owner_user_id)
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Owner user with ID {data.owner_user_id} not found"
        )

    # 2. Check if GST number already exists (if provided)
    if data.gst_no:
        existing_gst = db.query(models.Restaurant).filter(
            models.Restaurant.gst_no == data.gst_no,
            models.Restaurant.is_deleted == False
        ).first()
        if existing_gst:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Restaurant with GST number '{data.gst_no}' already exists"
            )

    # 3. Create the restaurant
    restaurant_data = data.model_dump()
    restaurant = models.Restaurant(**restaurant_data)
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)

    # 4. Automatic default-outlet logic:
    # Build clean code prefix from restaurant name
    prefix = "".join(c for c in restaurant.name.upper() if c.isalnum())[:4] or "REST"
    default_code = f"{prefix}-{restaurant.id:04d}-MAIN"

    # Ensure outlet_code uniqueness
    existing_outlet = db.query(models.Outlet).filter(models.Outlet.outlet_code == default_code).first()
    if existing_outlet:
        default_code = f"OUT-{restaurant.id:04d}-{uuid.uuid4().hex[:4].upper()}"

    default_outlet = models.Outlet(
        restaurant_id=restaurant.id,
        name=f"{restaurant.name} - Main Branch",
        outlet_code=default_code,
        is_default=True,
        status="ACTIVE"
    )
    db.add(default_outlet)
    db.commit()

    return restaurant


@router.get("/", response_model=List[RestaurantResponse])
def get_restaurants(db: Session = Depends(get_db)):
    """
    Retrieve all active (non-deleted) restaurants.
    """
    return db.query(models.Restaurant).filter(
        models.Restaurant.is_deleted == False
    ).all()


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific restaurant by its ID.
    """
    restaurant = db.query(models.Restaurant).filter(
        models.Restaurant.id == restaurant_id,
        models.Restaurant.is_deleted == False
    ).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    return restaurant


@router.put("/{restaurant_id}", response_model=RestaurantResponse)
def update_restaurant(restaurant_id: int, data: RestaurantUpdate, db: Session = Depends(get_db)):
    """
    Update restaurant details.
    """
    restaurant = db.query(models.Restaurant).filter(
        models.Restaurant.id == restaurant_id,
        models.Restaurant.is_deleted == False
    ).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )

    update_dict = data.model_dump(exclude_unset=True)

    # Check GST uniqueness if being updated
    if "gst_no" in update_dict and update_dict["gst_no"] != restaurant.gst_no:
        existing_gst = db.query(models.Restaurant).filter(
            models.Restaurant.gst_no == update_dict["gst_no"],
            models.Restaurant.id != restaurant_id,
            models.Restaurant.is_deleted == False
        ).first()
        if existing_gst:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Restaurant with GST number '{update_dict['gst_no']}' already exists"
            )

    for key, value in update_dict.items():
        setattr(restaurant, key, value)

    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.delete("/{restaurant_id}")
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    """
    Soft-delete a restaurant.
    """
    restaurant = db.query(models.Restaurant).filter(
        models.Restaurant.id == restaurant_id,
        models.Restaurant.is_deleted == False
    ).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )

    restaurant.is_deleted = True
    db.commit()
    return {"message": "Restaurant soft-deleted successfully"}
