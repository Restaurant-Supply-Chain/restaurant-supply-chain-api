from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from db import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    owner_user_id = Column(Integer)
    name = Column(String(120))
    legal_name = Column(String(150))
    cuisine_type = Column(String(100))
    gst_no = Column(String(20))
    fssai_no = Column(String(30))
    contact_email = Column(String(150))
    contact_phone = Column(String(15))
    status = Column(String(20), default="ACTIVE")
    credit_limit = Column(Float, default=0)
    payment_terms_days = Column(Integer, default=0)


class Outlet(Base):
    __tablename__ = "outlets"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    name = Column(String(120))
    outlet_code = Column(String(50))
    is_default = Column(Boolean, default=False)
    status = Column(String(20), default="ACTIVE")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    owner_type = Column(String(20))
    owner_id = Column(Integer)
    label = Column(String(100))
    line1 = Column(String(200))
    line2 = Column(String(200))
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    country = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    is_default = Column(Boolean, default=False)


class RestaurantStaff(Base):
    __tablename__ = "restaurant_staff"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    user_id = Column(Integer)
    role = Column(String(20))
    status = Column(String(20), default="ACTIVE")


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    requested_by = Column(Integer)
    request_type = Column(String(100))
    description = Column(String(500))
    status = Column(String(20), default="PENDING")
