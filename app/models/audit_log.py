from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, JSON, String, func

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True)
    actor_id = Column(BigInteger, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(80), nullable=False)
    entity = Column(String(80), nullable=False)
    entity_id = Column(BigInteger, nullable=True)
    before_json = Column(JSON(none_as_null=True), nullable=True)
    after_json = Column(JSON(none_as_null=True), nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
