from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String

from app.db.base import Base


class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    otp_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
