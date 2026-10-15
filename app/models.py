from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    legal_name = Column(String(150))
    cuisine_type = Column(String(100))
    gst_no = Column(String(15), unique=True, nullable=True)
    fssai_no = Column(String(14))
    contact_email = Column(String(100))
    contact_phone = Column(String(20))
    logo_url = Column(String(255))
    status = Column(String(20), default="ACTIVE")
    credit_limit = Column(Float, default=0)
    payment_terms_days = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)


class Outlet(Base):
    __tablename__ = "outlets"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String(100), nullable=False)
    outlet_code = Column(String(50), unique=True, nullable=False)
    is_default = Column(Boolean, default=False)
    status = Column(String(20), default="ACTIVE")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    owner_type = Column(String(20), nullable=False)
    owner_id = Column(Integer, nullable=False)
    label = Column(String(50))
    line1 = Column(String(200), nullable=False)
    line2 = Column(String(200))
    city = Column(String(100), nullable=False)
    state = Column(String(100))
    pincode = Column(String(10))
    country = Column(String(100), default="India")
    latitude = Column(Float)
    longitude = Column(Float)
    is_default = Column(Boolean, default=False)


class RestaurantStaff(Base):
    __tablename__ = "restaurant_staff"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default="STAFF")
    status = Column(String(20), default="ACTIVE")


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    request_type = Column(String(50), nullable=False)
    status = Column(String(20), default="PENDING")
    remarks = Column(String(255))
