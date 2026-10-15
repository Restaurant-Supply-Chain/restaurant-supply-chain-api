from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, JSON, String, Text

from app.db.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(80), nullable=False)
    title = Column(String(120), nullable=False)
    body = Column(Text, nullable=False)
    payload_json = Column(JSON(none_as_null=True), nullable=True)
    channel = Column(String(20), nullable=False, default="IN_APP", server_default="IN_APP")
    read_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
