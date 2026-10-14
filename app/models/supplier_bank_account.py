from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey
from app.db.base import Base


class SupplierBankAccount(Base):
    __tablename__ = "supplier_bank_accounts"

    id = Column(BigInteger, primary_key=True, index=True)
    supplier_id = Column(
        BigInteger,
        ForeignKey("suppliers.id"),
        nullable=False,
    )
    account_holder = Column(String(160), nullable=False)
    account_no = Column(String(50), nullable=False)
    ifsc = Column(String(11), nullable=False)
    bank_name = Column(String(160), nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)