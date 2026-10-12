from uuid import uuid4

from sqlalchemy import BigInteger, Boolean, CHAR, Column, DateTime, Enum, Integer, String, text

from app.core.constants import UserRole, UserStatus
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    uuid = Column(CHAR(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    email = Column(String(254), unique=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=False)
    role = Column(Enum(UserRole, name="user_role"), nullable=False)
    status = Column(
        Enum(UserStatus, name="user_status"),
        nullable=False,
        default=UserStatus.PENDING,
        server_default="PENDING",
    )
    email_verified = Column(Boolean, nullable=False, default=False, server_default=text("0"))
    phone_verified = Column(Boolean, nullable=False, default=False, server_default=text("0"))
    last_login_at = Column(DateTime, nullable=True)
    failed_login_count = Column(Integer, nullable=False, default=0, server_default=text("0"))
    locked_until = Column(DateTime, nullable=True)
