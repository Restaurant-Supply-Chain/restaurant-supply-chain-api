from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.core.constants import UserRole, UserStatus
from app.core.security import create_token
from app.main import app


def profile(client, token):
    return client.get("/auth/me", headers={"Authorization": "Bearer " + token})


def test_me_returns_current_user_without_password(client, db, login_tokens):
    user, tokens = login_tokens
    response = profile(client, tokens["access_token"])
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == user.id and result["uuid"] == user.uuid
    assert result["email"] == user.email and result["role"] == user.role.value
    assert "password" not in result and "password_hash" not in result
    user.role = UserRole.DRIVER
    db.commit()
    assert profile(client, tokens["access_token"]).json()["role"] == "DRIVER"


def test_me_rejects_missing_wrong_and_expired_tokens(client, login_tokens):
    user, tokens = login_tokens
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    expired = create_token(user.uuid, "access", now - timedelta(minutes=1))
    unknown_user = create_token(str(uuid4()), "access", now + timedelta(minutes=15))
    invalid_headers = [
        {},
        {"Authorization": "Basic invalid"},
        {"Authorization": "Bearer not-a-token"},
        {"Authorization": "Bearer " + tokens["refresh_token"]},
        {"Authorization": "Bearer " + tokens["access_token"] + ".broken"},
        {"Authorization": "Bearer " + expired},
        {"Authorization": "Bearer " + unknown_user},
    ]
    for headers in invalid_headers:
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"
        assert response.headers["content-type"] == "application/problem+json"


def test_me_rejects_non_active_accounts(client, db, login_tokens):
    user, tokens = login_tokens
    for status in [UserStatus.PENDING, UserStatus.INACTIVE, UserStatus.SUSPENDED]:
        user.status = status
        db.commit()
        assert profile(client, tokens["access_token"]).status_code == 403


def test_me_has_bearer_auth_in_swagger():
    operation = app.openapi()["paths"]["/auth/me"]["get"]
    assert operation["security"] == [{"HTTPBearer": []}]
