from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Date,
    Numeric,
    ForeignKey,
    Enum,
)
from app.db.base import Base


class SupplierContract(Base):
    __tablename__ = "supplier_contracts"

    id = Column(BigInteger, primary_key=True, index=True)

    supplier_id = Column(
        BigInteger,
        ForeignKey("suppliers.id"),
        nullable=False,
    )

    restaurant_id = Column(
        BigInteger,
        ForeignKey("restaurants.id"),
        nullable=False,
    )

    contract_no = Column(String(50), unique=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    payment_terms = Column(String(255), nullable=True)
    discount_pct = Column(Numeric(5, 2), default=0)

    status = Column(
        Enum(
            "DRAFT",
            "ACTIVE",
            "EXPIRED",
            "TERMINATED",
            name="supplier_contract_status",
        ),
        default="DRAFT",
        nullable=False,
    )