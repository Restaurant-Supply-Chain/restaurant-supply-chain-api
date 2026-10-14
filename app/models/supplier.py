from sqlalchemy import Column, BigInteger, String, Numeric, Integer, Time, ForeignKey, Enum
from app.db.base import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(BigInteger, primary_key=True, index=True)
    owner_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    cutoff_time = Column(Time, nullable=True)
    business_name = Column(String(160), nullable=False)
    legal_name = Column(String(160), nullable=True)
    gst_no = Column(String(15), unique=True, nullable=True)
    fssai_no = Column(String(14), nullable=True)
    pan_no = Column(String(10), nullable=True)
    category = Column(
    Enum("FOOD", "BEVERAGE", "PACKAGING", "EQUIPMENT", "MIXED", name="supplier_category"),
    nullable=False,
)
    contact_email = Column(String(254), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    min_order_value = Column(Numeric(12, 2), default=0)
    delivery_radius_km = Column(Integer, nullable=True)
    rating = Column(Numeric(3, 2), default=0)
    status = Column(
    Enum("PENDING", "ACTIVE", "SUSPENDED", "BLACKLISTED", name="supplier_status"),
    default="PENDING",
    nullable=False,
)