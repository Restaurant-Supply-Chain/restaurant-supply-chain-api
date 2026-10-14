from sqlalchemy import Column, BigInteger, String, ForeignKey
from app.db.base import Base


class Distributor(Base):
    __tablename__ = "distributors"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(160), nullable=False)
    region = Column(String(160), nullable=True)
    contact = Column(String(100), nullable=True)
    parent_supplier_id = Column(
        BigInteger,
        ForeignKey("suppliers.id"),
        nullable=True,
    )