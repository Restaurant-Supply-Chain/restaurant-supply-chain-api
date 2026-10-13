import hashlib
from datetime import timezone
from uuid import uuid4

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password):
    return password_context.hash(password)


def verify_password(password, password_hash):
    return password_context.verify(password, password_hash)


def create_token(user_uuid, token_type, expires_at):
    payload = {
        "sub": user_uuid,
        "type": token_type,
        "jti": str(uuid4()),
        "exp": int(expires_at.replace(tzinfo=timezone.utc).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def hash_token(token):
    # Store a hash so the database does not contain usable refresh tokens.
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
