from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from jose import jwt

from app.core.config import settings
from app.core.constants import UserRole, UserStatus
from app.core.security import hash_password, hash_token
from app.main import app
from app.models.refresh_token import RefreshToken
from app.models.user import User


@pytest.fixture
def user(db):
    user = User(
        full_name="Login Test",
        email=uuid4().hex + "@example.com",
        password_hash=hash_password("Practice123!"),
        role=UserRole.RESTAURANT_ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    db.commit()
    return user


def login(client, user, password="Practice123!"):
    return client.post("/auth/login", json={"email": user.email, "password": password})


def test_login_returns_tokens_with_correct_expiry(client, db, user):
    user.failed_login_count = 2
    db.commit()
    before = int(datetime.now(timezone.utc).timestamp())
    response = client.post("/auth/login", json={
        "email": "  " + user.email.upper() + "  ", "password": "Practice123!",
    })
    assert response.status_code == 200
    result = response.json()
    assert result["token_type"] == "bearer" and result["expires_in"] == 900
    for token_type, lifetime in [("access", 900), ("refresh", 7 * 24 * 60 * 60)]:
        claims = jwt.decode(result[token_type + "_token"], settings.JWT_SECRET_KEY,
                            algorithms=[settings.JWT_ALGORITHM])
        assert claims["sub"] == user.uuid and claims["type"] == token_type
        assert before + lifetime <= claims["exp"] <= before + lifetime + 5
    stored = db.query(RefreshToken).filter_by(user_id=user.id).one()
    assert stored.token_hash == hash_token(result["refresh_token"])
    assert stored.token_hash != result["refresh_token"] and stored.revoked_at is None
    assert stored.user_agent and stored.ip_address
    assert user.last_login_at and user.failed_login_count == 0


def test_unknown_email_and_wrong_password_have_same_error(client, db, user):
    unknown = client.post("/auth/login", json={"email": "missing@example.com", "password": "Wrong123!"})
    wrong = login(client, user, "Wrong123!")
    assert unknown.status_code == wrong.status_code == 401
    assert unknown.json()["detail"] == wrong.json()["detail"]
    assert wrong.headers["content-type"] == "application/problem+json"
    assert user.failed_login_count == 1
    assert db.query(RefreshToken).filter_by(user_id=user.id).count() == 0


def test_failed_attempts_lock_account(client, user):
    for _ in range(settings.LOGIN_MAX_ATTEMPTS):
        assert login(client, user, "Wrong123!").status_code == 401
    assert user.failed_login_count == settings.LOGIN_MAX_ATTEMPTS
    remaining = user.locked_until - datetime.now(timezone.utc).replace(tzinfo=None)
    lock_seconds = settings.LOGIN_LOCK_MINUTES * 60
    # MySQL rounds DATETIME values to whole seconds.
    assert lock_seconds - 5 <= remaining.total_seconds() <= lock_seconds + 1
    blocked = login(client, user)
    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) > 0


def test_expired_lock_allows_login(client, db, user):
    user.locked_until = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=1)
    user.failed_login_count = settings.LOGIN_MAX_ATTEMPTS
    db.commit()
    assert login(client, user).status_code == 200
    assert user.locked_until is None and user.failed_login_count == 0


@pytest.mark.parametrize("status", [UserStatus.PENDING, UserStatus.INACTIVE, UserStatus.SUSPENDED])
def test_non_active_user_cannot_login(client, db, user, status):
    user.status = status
    db.commit()
    assert login(client, user).status_code == 403
    assert db.query(RefreshToken).filter_by(user_id=user.id).count() == 0


def test_login_rejects_overlong_password(client, user):
    assert login(client, user, "Practice123!" + "x" * 72).status_code == 422


def test_auth_endpoints_are_documented():
    paths = app.openapi()["paths"]
    assert "post" in paths["/auth/register"]
    assert "post" in paths["/auth/login"]
