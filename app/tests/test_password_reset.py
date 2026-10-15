import re
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.constants import UserStatus
from app.core.security import verify_password
from app.main import app
from app.models.password_reset import PasswordReset
from app.models.refresh_token import RefreshToken


def request_otp(client, email, capsys):
    capsys.readouterr()
    response = client.post("/auth/forgot-password", json={"email": email})
    assert response.status_code == 200 and "otp" not in response.json()
    output = capsys.readouterr().out
    return re.search(r"OTP: ([0-9]{6})", output).group(1)


def reset(client, email, otp, password="Changed123!"):
    return client.post("/auth/reset-password", json={
        "email": email, "otp": otp, "new_password": password,
    })


def test_reset_changes_password_once_and_revokes_sessions(client, db, login_tokens, capsys):
    user, tokens = login_tokens
    otp = request_otp(client, "  " + user.email.upper() + "  ", capsys)
    record = db.query(PasswordReset).filter_by(user_id=user.id).one()
    assert record.otp_hash != otp and verify_password(otp, record.otp_hash)
    remaining = record.expires_at - datetime.now(timezone.utc).replace(tzinfo=None)
    assert 895 <= remaining.total_seconds() <= 901
    user.failed_login_count = 5
    user.locked_until = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=15)
    db.commit()
    assert reset(client, user.email, otp).status_code == 200
    assert user.failed_login_count == 0 and user.locked_until is None
    assert record.used_at is not None
    assert reset(client, user.email, otp).status_code == 400
    assert db.query(RefreshToken).filter_by(user_id=user.id, revoked_at=None).count() == 0
    assert client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401
    assert client.post("/auth/login", json={"email": user.email, "password": "Practice123!"}).status_code == 401
    assert client.post("/auth/login", json={"email": user.email, "password": "Changed123!"}).status_code == 200


def test_new_request_invalidates_previous_otp(client, db, login_tokens, capsys, monkeypatch):
    user, _ = login_tokens
    codes = iter([123456, 654321])
    monkeypatch.setattr("app.services.auth.secrets.randbelow", lambda limit: next(codes))
    old_otp = request_otp(client, user.email, capsys)
    new_otp = request_otp(client, user.email, capsys)
    assert old_otp != new_otp
    assert reset(client, user.email, old_otp).status_code == 400
    assert reset(client, user.email, new_otp).status_code == 200


def test_wrong_expired_and_invalid_inputs_do_not_change_password(client, db, login_tokens, capsys):
    user, _ = login_tokens
    otp = request_otp(client, user.email, capsys)
    original_hash = user.password_hash
    wrong_otp = "000000" if otp != "000000" else "111111"
    wrong = reset(client, user.email, wrong_otp)
    assert wrong.status_code == 400
    assert wrong.headers["content-type"] == "application/problem+json"
    assert reset(client, user.email, "abc123").status_code == 422
    assert reset(client, user.email, otp, "weak").status_code == 422
    record = db.query(PasswordReset).filter_by(user_id=user.id).one()
    record.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)
    db.commit()
    assert reset(client, user.email, otp).status_code == 400
    assert record.used_at is None and user.password_hash == original_hash


def test_forgot_password_does_not_reveal_unknown_or_inactive_accounts(client, db, login_tokens, capsys):
    user, _ = login_tokens
    unknown = client.post("/auth/forgot-password", json={"email": "missing@example.com"})
    active = client.post("/auth/forgot-password", json={"email": user.email})
    assert unknown.status_code == active.status_code == 200
    assert unknown.json() == active.json()
    capsys.readouterr()
    user.status = UserStatus.SUSPENDED
    db.commit()
    inactive = client.post("/auth/forgot-password", json={"email": user.email})
    assert inactive.json() == unknown.json()
    assert "OTP:" not in capsys.readouterr().out


def test_console_delivery_is_disabled_outside_debug_mode(client, monkeypatch):
    monkeypatch.setattr(settings, "DEBUG", False)
    response = client.post("/auth/forgot-password", json={"email": "missing@example.com"})
    assert response.status_code == 503


def test_reset_endpoints_are_documented():
    paths = app.openapi()["paths"]
    assert "post" in paths["/auth/forgot-password"]
    assert "post" in paths["/auth/reset-password"]
