from datetime import datetime, timedelta, timezone

from app.core.constants import UserStatus
from app.core.security import hash_token
from app.main import app
from app.models.refresh_token import RefreshToken


def logout(client, token):
    return client.post("/auth/logout", json={"refresh_token": token})


def test_logout_revokes_only_the_supplied_session(client, db, login_tokens):
    user, tokens = login_tokens
    other_session = client.post("/auth/login", json={
        "email": user.email, "password": "Practice123!",
    }).json()
    response = logout(client, tokens["refresh_token"])
    assert response.status_code == 204 and response.content == b""
    stored = db.query(RefreshToken).filter_by(token_hash=hash_token(tokens["refresh_token"])).one()
    revoked_at = stored.revoked_at
    assert revoked_at is not None
    assert logout(client, tokens["refresh_token"]).status_code == 204
    assert stored.revoked_at == revoked_at
    assert client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401
    assert client.post("/auth/refresh", json={"refresh_token": other_session["refresh_token"]}).status_code == 200


def test_logout_rejects_invalid_access_and_expired_tokens(client, db, login_tokens):
    _, tokens = login_tokens
    for token in ["not-a-token", tokens["access_token"]]:
        response = logout(client, token)
        assert response.status_code == 401
        assert response.headers["content-type"] == "application/problem+json"
    stored = db.query(RefreshToken).filter_by(token_hash=hash_token(tokens["refresh_token"])).one()
    stored.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)
    db.commit()
    assert logout(client, tokens["refresh_token"]).status_code == 401
    assert stored.revoked_at is None


def test_suspended_account_can_still_logout(client, db, login_tokens):
    user, tokens = login_tokens
    user.status = UserStatus.SUSPENDED
    db.commit()
    assert logout(client, tokens["refresh_token"]).status_code == 204


def test_logout_is_documented():
    assert "post" in app.openapi()["paths"]["/auth/logout"]
