from sqlalchemy import Column, Integer, String

from app.db.base import Base


class SalesOrder(Base):
    __tablename__ = "sales_orders"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, nullable=False)
    supplier_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(
        String(20),
        nullable=False,
        default="pending",
    )
