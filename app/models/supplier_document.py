from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey, DateTime
from app.db.base import Base


class SupplierDocument(Base):
    __tablename__ = "supplier_documents"

    id = Column(BigInteger, primary_key=True, index=True)

    supplier_id = Column(
        BigInteger,
        ForeignKey("suppliers.id"),
        nullable=False,
    )

    doc_type = Column(String(50), nullable=False)
    file_url = Column(String(500), nullable=False)
    verified = Column(Boolean, default=False, nullable=False)

    verified_by = Column(BigInteger, nullable=True)
    expires_at = Column(DateTime, nullable=True)