from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings
from app.core.constants import UserStatus
from app.core.security import create_token, hash_token
from app.main import app
from app.models.refresh_token import RefreshToken


def refresh(client, token):
    return client.post("/auth/refresh", json={"refresh_token": token})


def test_refresh_rotates_tokens_and_rejects_reuse(client, db, login_tokens):
    user, original = login_tokens
    before = int(datetime.now(timezone.utc).timestamp())
    response = refresh(client, original["refresh_token"])
    assert response.status_code == 200
    replacement = response.json()
    assert replacement["access_token"] != original["access_token"]
    assert replacement["refresh_token"] != original["refresh_token"]
    for kind, lifetime in [("access", 900), ("refresh", 7 * 24 * 60 * 60)]:
        claims = jwt.decode(replacement[kind + "_token"], settings.JWT_SECRET_KEY,
                            algorithms=[settings.JWT_ALGORITHM])
        assert claims["sub"] == user.uuid and claims["type"] == kind
        assert before + lifetime <= claims["exp"] <= before + lifetime + 5
    old = db.query(RefreshToken).filter_by(token_hash=hash_token(original["refresh_token"])).one()
    assert old.revoked_at is not None
    rejected = refresh(client, original["refresh_token"])
    assert rejected.status_code == 401
    assert rejected.headers["content-type"] == "application/problem+json"
    assert refresh(client, replacement["refresh_token"]).status_code == 200


def test_invalid_and_access_tokens_are_rejected(client, login_tokens):
    _, tokens = login_tokens
    for token in ["not-a-token", tokens["access_token"], tokens["refresh_token"] + ".broken"]:
        assert refresh(client, token).status_code == 401


def test_expired_tokens_are_rejected(client, db, login_tokens):
    user, tokens = login_tokens
    past = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)
    stored = db.query(RefreshToken).filter_by(token_hash=hash_token(tokens["refresh_token"])).one()
    stored.expires_at = past
    db.commit()
    assert refresh(client, tokens["refresh_token"]).status_code == 401
    assert stored.revoked_at is None

    # Also check JWT expiry independently of the database expiry.
    expired_jwt = create_token(user.uuid, "refresh", past)
    db.add(RefreshToken(user_id=user.id, token_hash=hash_token(expired_jwt),
                        expires_at=past + timedelta(days=7)))
    db.commit()
    assert refresh(client, expired_jwt).status_code == 401


def test_inactive_account_cannot_refresh(client, db, login_tokens):
    user, tokens = login_tokens
    user.status = UserStatus.SUSPENDED
    db.commit()
    assert refresh(client, tokens["refresh_token"]).status_code == 403


def test_refresh_is_documented():
    assert "post" in app.openapi()["paths"]["/auth/refresh"]
