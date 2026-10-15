import math
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from jose import JWTError
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.constants import UserStatus
from app.core.security import create_token, decode_token, hash_password, hash_token, verify_password
from app.crud.user import create_user, get_user_by_email, get_user_by_phone, get_user_for_login
from app.models.refresh_token import RefreshToken
from app.models.password_reset import PasswordReset
from app.models.user import User


def register_user(db, data):
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="Email is already registered.")
    if data.phone and get_user_by_phone(db, data.phone):
        raise HTTPException(status_code=409, detail="Phone is already registered.")

    password_hash = hash_password(data.password)
    try:
        return create_user(db, data, password_hash)
    # Concurrent registrations can still hit the database uniqueness rule.
    except IntegrityError as error:
        db.rollback()
        # MySQL error 1062 means another request inserted the same unique value.
        if error.orig.args[0] == 1062:
            raise HTTPException(status_code=409, detail="Email or phone is already registered.") from error
        raise


def login_user(db, data, ip_address=None, user_agent=None):
    # MySQL DATETIME values are stored as UTC without timezone information.
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    user = get_user_for_login(db, data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if user.locked_until and user.locked_until > now:
        retry_after = math.ceil((user.locked_until - now).total_seconds())
        raise HTTPException(status_code=429, detail="Account is temporarily locked.",
                            headers={"Retry-After": str(retry_after)})

    # Start a fresh attempt count after a previous lock has expired.
    if user.locked_until:
        user.locked_until = None
        user.failed_login_count = 0

    if not verify_password(data.password, user.password_hash):
        user.failed_login_count += 1
        if user.failed_login_count >= settings.LOGIN_MAX_ATTEMPTS:
            user.locked_until = now + timedelta(minutes=settings.LOGIN_LOCK_MINUTES)
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=403, detail="Account must be active to log in.")

    tokens = issue_tokens(db, user, now, ip_address, user_agent)
    user.failed_login_count = 0
    user.locked_until = None
    user.last_login_at = now
    db.commit()
    return tokens


def issue_tokens(db, user, now, ip_address, user_agent):
    # Login and refresh use the same token lifetimes and storage rules.
    access_expiry = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expiry = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    access_token = create_token(user.uuid, "access", access_expiry)
    refresh_token = create_token(user.uuid, "refresh", refresh_expiry)
    db.add(RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=refresh_expiry,
        ip_address=ip_address,
        user_agent=user_agent[:255] if user_agent else None,
    ))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


def refresh_user_tokens(db, data, ip_address=None, user_agent=None):
    try:
        claims = decode_token(data.refresh_token, "refresh")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    # Lock the user first, matching login's lock order.
    user = db.query(User).filter(User.uuid == claims["sub"]).with_for_update().first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == hash_token(data.refresh_token),
        RefreshToken.user_id == user.id,
    ).with_for_update().first()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if not stored_token or stored_token.revoked_at or stored_token.expires_at <= now:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=403, detail="Account must be active to refresh tokens.")

    # Revoke the old token and save its replacement in the same transaction.
    stored_token.revoked_at = now
    tokens = issue_tokens(db, user, now, ip_address, user_agent)
    db.commit()
    return tokens


def logout_user(db, data):
    try:
        claims = decode_token(data.refresh_token, "refresh")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    user = db.query(User).filter(User.uuid == claims["sub"]).with_for_update().first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == hash_token(data.refresh_token),
        RefreshToken.user_id == user.id,
    ).with_for_update().first()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if not stored_token or stored_token.expires_at <= now:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    # Repeated logout succeeds without changing the original revocation time.
    if stored_token.revoked_at is None:
        stored_token.revoked_at = now
    db.commit()


def forgot_password(db, data):
    # Console delivery is only for this local practice project.
    if not settings.DEBUG:
        raise HTTPException(status_code=503, detail="Password reset delivery is not configured.")

    message = {"message": "If an active account exists, password reset instructions have been generated."}
    user = get_user_for_login(db, data.email)
    if not user or user.status != UserStatus.ACTIVE:
        return message

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    # A new request invalidates any older unused OTPs.
    db.query(PasswordReset).filter(
        PasswordReset.user_id == user.id, PasswordReset.used_at.is_(None),
    ).update({PasswordReset.used_at: now}, synchronize_session="fetch")
    otp = str(secrets.randbelow(1_000_000)).zfill(6)
    db.add(PasswordReset(
        user_id=user.id,
        otp_hash=hash_password(otp),
        expires_at=now + timedelta(minutes=15),
    ))
    db.commit()
    print(f"Password reset for {user.email} - OTP: {otp}", flush=True)
    return message


def reset_password(db, data):
    invalid_otp = HTTPException(status_code=400, detail="Invalid or expired OTP.")
    user = get_user_for_login(db, data.email)
    if not user or user.status != UserStatus.ACTIVE:
        raise invalid_otp

    reset = db.query(PasswordReset).filter(
        PasswordReset.user_id == user.id, PasswordReset.used_at.is_(None),
    ).order_by(PasswordReset.id.desc()).with_for_update().first()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if not reset or reset.expires_at <= now or not verify_password(data.otp, reset.otp_hash):
        raise invalid_otp

    user.password_hash = hash_password(data.new_password)
    user.failed_login_count = 0
    user.locked_until = None
    reset.used_at = now
    # Revoke existing refresh sessions when the password changes.
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None),
    ).update({RefreshToken.revoked_at: now}, synchronize_session="fetch")
    db.commit()
    return {"message": "Password reset successfully."}
