import json
import re
from uuid import uuid4

import pytest

from app.core.config import settings
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.models.user import User


def test_auth_events_and_welcome_message_are_stored(client, db, login_tokens):
    user, tokens = login_tokens
    refreshed = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refreshed.status_code == 200
    refresh_token = refreshed.json()["refresh_token"]
    assert client.post("/auth/logout", json={"refresh_token": refresh_token}).status_code == 204
    assert client.post("/auth/logout", json={"refresh_token": refresh_token}).status_code == 204
    logs = db.query(AuditLog).filter_by(entity_id=user.id, entity="users").all()
    assert {log.action for log in logs} == {"USER_REGISTERED", "LOGIN_SUCCESS", "TOKEN_REFRESHED", "LOGOUT"}
    assert sum(log.action == "LOGOUT" for log in logs) == 1
    assert all(log.actor_id == user.id and log.created_at and log.ip_address for log in logs)
    welcome = db.query(Notification).filter_by(user_id=user.id, type="WELCOME").one()
    assert welcome.channel == "IN_APP" and welcome.read_at is None and welcome.sent_at


def test_failed_logins_create_one_lockout_message(client, db, login_tokens):
    user, _ = login_tokens
    for _ in range(settings.LOGIN_MAX_ATTEMPTS):
        response = client.post("/auth/login", json={"email": user.email, "password": "Wrong123!"})
        assert response.status_code == 401
    assert db.query(AuditLog).filter_by(entity_id=user.id, action="LOGIN_FAILED").count() == settings.LOGIN_MAX_ATTEMPTS
    assert db.query(Notification).filter_by(user_id=user.id, type="ACCOUNT_LOCKED").count() == 1
    blocked = client.post("/auth/login", json={"email": user.email, "password": "Practice123!"})
    assert blocked.status_code == 429
    assert db.query(Notification).filter_by(user_id=user.id, type="ACCOUNT_LOCKED").count() == 1


def test_password_reset_events_do_not_store_secrets(client, db, login_tokens, capsys):
    user, tokens = login_tokens
    capsys.readouterr()
    assert client.post("/auth/forgot-password", json={"email": user.email}).status_code == 200
    otp = re.search(r"OTP: ([0-9]{6})", capsys.readouterr().out).group(1)
    assert client.post("/auth/reset-password", json={
        "email": user.email, "otp": otp, "new_password": "Changed123!",
    }).status_code == 200
    logs = db.query(AuditLog).filter_by(entity_id=user.id, entity="users").all()
    actions = {log.action for log in logs}
    assert {"PASSWORD_RESET_REQUESTED", "PASSWORD_RESET_SUCCESS"} <= actions
    snapshots = json.dumps([{ "before": log.before_json, "after": log.after_json } for log in logs])
    for secret in ["Practice123!", "Changed123!", otp, tokens["access_token"], tokens["refresh_token"], user.password_hash]:
        assert secret not in snapshots
    changed = db.query(Notification).filter_by(user_id=user.id, type="PASSWORD_CHANGED").one()
    assert changed.read_at is None and changed.payload_json is None
    assert otp not in changed.body and "Changed123!" not in changed.body


def test_registration_rolls_back_if_related_records_fail(client, db, monkeypatch):
    email = uuid4().hex + "@example.com"

    def fail_notification(*args, **kwargs):
        raise RuntimeError("Simulated notification failure")

    monkeypatch.setattr("app.services.auth.create_notification", fail_notification)
    with pytest.raises(RuntimeError, match="Simulated notification failure"):
        client.post("/auth/register", json={
            "full_name": "Rollback Test", "email": email, "password": "Practice123!",
        })
    db.rollback()
    assert db.query(User).filter_by(email=email).count() == 0
    assert db.query(AuditLog).filter(AuditLog.after_json["email"].as_string() == email).count() == 0
