from typing import List
from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app import models
from app.schemas.user import UserCreate, UserResponse
from app.routers import restaurant_router, outlet_router, address_router

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Restaurant Supply Chain API",
    description="FastAPI service for managing restaurants, outlets, and addresses with automatic default outlet provisioning.",
    version="1.0.0"
)

# Connect all three routers using app.include_router()
app.include_router(restaurant_router)
app.include_router(outlet_router)
app.include_router(address_router)


@app.get("/", tags=["Health"])
def home():
    return {
        "message": "Restaurant Supply Chain API running",
        "docs_url": "/docs"
    }


# Helper endpoints for User management (needed for owner_user_id references)
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a user to serve as restaurant owner.
    """
    user = models.User(**data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/users/", response_model=List[UserResponse], tags=["Users"])
def get_users(db: Session = Depends(get_db)):
    """
    Retrieve all users.
    """
    return db.query(models.User).all()