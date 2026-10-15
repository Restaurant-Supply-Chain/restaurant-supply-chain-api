from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from app.db import Base, engine, get_db
from app import models, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Restaurant Supply Chain API")

restaurant_router = APIRouter(prefix="/restaurants", tags=["Restaurants"])
outlet_router = APIRouter(prefix="/outlets", tags=["Outlets"])
address_router = APIRouter(prefix="/addresses", tags=["Addresses"])
staff_router = APIRouter(prefix="/restaurant-staff", tags=["Restaurant Staff"])
approval_router = APIRouter(prefix="/approval-requests", tags=["Approval Requests"])


@app.get("/")
def home():
    return {"message": "Restaurant Supply Chain API running"}


@app.post("/users/", tags=["Users"])
def create_user(data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = models.User(**data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# RESTAURANTS
@restaurant_router.post("/")
def create_restaurant(data: schemas.RestaurantCreate,
                      db: Session = Depends(get_db)):
    if not db.get(models.User, data.owner_user_id):
        raise HTTPException(404, "Owner user not found")

    restaurant = models.Restaurant(**data.model_dump())
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant


@restaurant_router.get("/")
def get_restaurants(db: Session = Depends(get_db)):
    return db.query(models.Restaurant).filter(
        models.Restaurant.is_deleted == False
    ).all()


@restaurant_router.get("/{restaurant_id}")
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(models.Restaurant).filter(
        models.Restaurant.id == restaurant_id,
        models.Restaurant.is_deleted == False
    ).first()
    if not restaurant:
        raise HTTPException(404, "Restaurant not found")
    return restaurant


@restaurant_router.put("/{restaurant_id}")
def update_restaurant(restaurant_id: int, data: schemas.RestaurantUpdate,
                      db: Session = Depends(get_db)):
    restaurant = db.query(models.Restaurant).filter(
        models.Restaurant.id == restaurant_id,
        models.Restaurant.is_deleted == False
    ).first()
    if not restaurant:
        raise HTTPException(404, "Restaurant not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(restaurant, key, value)
    db.commit()
    db.refresh(restaurant)
    return restaurant


@restaurant_router.delete("/{restaurant_id}")
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(models.Restaurant).filter(
        models.Restaurant.id == restaurant_id,
        models.Restaurant.is_deleted == False
    ).first()
    if not restaurant:
        raise HTTPException(404, "Restaurant not found")

    restaurant.is_deleted = True
    db.commit()
    return {"message": "Restaurant soft-deleted successfully"}


# OUTLETS
@outlet_router.post("/")
def create_outlet(data: schemas.OutletCreate, db: Session = Depends(get_db)):
    restaurant = db.query(models.Restaurant).filter(
        models.Restaurant.id == data.restaurant_id,
        models.Restaurant.is_deleted == False
    ).first()
    if not restaurant:
        raise HTTPException(404, "Restaurant not found")

    values = data.model_dump()
    outlets = db.query(models.Outlet).filter(
        models.Outlet.restaurant_id == data.restaurant_id
    ).all()

    # First outlet is always default
    if not outlets:
        values["is_default"] = True

    # Only one default outlet per restaurant
    if values["is_default"]:
        for outlet in outlets:
            outlet.is_default = False

    outlet = models.Outlet(**values)
    db.add(outlet)
    db.commit()
    db.refresh(outlet)
    return outlet


@outlet_router.get("/")
def get_outlets(db: Session = Depends(get_db)):
    return db.query(models.Outlet).all()


@outlet_router.get("/{outlet_id}")
def get_outlet(outlet_id: int, db: Session = Depends(get_db)):
    outlet = db.get(models.Outlet, outlet_id)
    if not outlet:
        raise HTTPException(404, "Outlet not found")
    return outlet


@outlet_router.put("/{outlet_id}")
def update_outlet(outlet_id: int, data: schemas.OutletUpdate,
                  db: Session = Depends(get_db)):
    outlet = db.get(models.Outlet, outlet_id)
    if not outlet:
        raise HTTPException(404, "Outlet not found")

    values = data.model_dump(exclude_unset=True)
    if values.get("is_default") is True:
        db.query(models.Outlet).filter(
            models.Outlet.restaurant_id == outlet.restaurant_id
        ).update({"is_default": False})

    for key, value in values.items():
        setattr(outlet, key, value)
    db.commit()
    db.refresh(outlet)
    return outlet


@outlet_router.delete("/{outlet_id}")
def delete_outlet(outlet_id: int, db: Session = Depends(get_db)):
    outlet = db.get(models.Outlet, outlet_id)
    if not outlet:
        raise HTTPException(404, "Outlet not found")

    was_default = outlet.is_default
    restaurant_id = outlet.restaurant_id
    db.delete(outlet)
    db.flush()

    if was_default:
        next_outlet = db.query(models.Outlet).filter(
            models.Outlet.restaurant_id == restaurant_id
        ).first()
        if next_outlet:
            next_outlet.is_default = True

    db.commit()
    return {"message": "Outlet deleted successfully"}


# ADDRESSES
@address_router.post("/")
def create_address(data: schemas.AddressCreate, db: Session = Depends(get_db)):
    address = models.Address(**data.model_dump())
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


@address_router.get("/")
def get_addresses(db: Session = Depends(get_db)):
    return db.query(models.Address).all()


@address_router.get("/{address_id}")
def get_address(address_id: int, db: Session = Depends(get_db)):
    address = db.get(models.Address, address_id)
    if not address:
        raise HTTPException(404, "Address not found")
    return address


@address_router.put("/{address_id}")
def update_address(address_id: int, data: schemas.AddressUpdate,
                   db: Session = Depends(get_db)):
    address = db.get(models.Address, address_id)
    if not address:
        raise HTTPException(404, "Address not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(address, key, value)
    db.commit()
    db.refresh(address)
    return address


@address_router.delete("/{address_id}")
def delete_address(address_id: int, db: Session = Depends(get_db)):
    address = db.get(models.Address, address_id)
    if not address:
        raise HTTPException(404, "Address not found")

    db.delete(address)
    db.commit()
    return {"message": "Address deleted successfully"}


# RESTAURANT STAFF
@staff_router.post("/")
def create_staff(data: schemas.StaffCreate, db: Session = Depends(get_db)):
    staff = models.RestaurantStaff(**data.model_dump())
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


@staff_router.get("/")
def get_staff(db: Session = Depends(get_db)):
    return db.query(models.RestaurantStaff).all()


# APPROVAL REQUESTS
@approval_router.post("/")
def create_approval(data: schemas.ApprovalCreate,
                    db: Session = Depends(get_db)):
    request = models.ApprovalRequest(**data.model_dump())
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@approval_router.get("/")
def get_approvals(db: Session = Depends(get_db)):
    return db.query(models.ApprovalRequest).all()


app.include_router(restaurant_router)
app.include_router(outlet_router)
app.include_router(address_router)
app.include_router(staff_router)
app.include_router(approval_router)