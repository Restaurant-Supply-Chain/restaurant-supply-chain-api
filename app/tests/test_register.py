from uuid import uuid4

import pytest

from app.core.security import verify_password
from app.models.user import User


@pytest.fixture
def payload():
    return {
        "full_name": "Dev One",
        "email": uuid4().hex + "@example.com",
        "password": "Practice123!",
        "role": "RESTAURANT_ADMIN",
    }


def test_registration_hashes_password_and_normalizes_email(client, db, payload):
    payload["email"] = "  " + payload["email"].upper() + "  "
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    result = response.json()
    assert result["email"] == payload["email"].strip().lower()
    assert result["status"] == "ACTIVE"
    assert "password" not in result and "password_hash" not in result
    user = db.get(User, result["id"])
    assert user.password_hash != payload["password"]
    assert verify_password(payload["password"], user.password_hash)


def test_duplicate_email_is_a_problem_response(client, payload):
    assert client.post("/auth/register", json=payload).status_code == 201
    payload["email"] = payload["email"].upper()
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["status"] == 409


@pytest.mark.parametrize("password", ["Short1!", "practice123!", "PRACTICE123!", "Practice!", "Practice123", "Aa1!" + "x" * 69])
def test_invalid_password_is_rejected(client, payload, password):
    payload["password"] = password
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    assert password not in response.text


@pytest.mark.parametrize("field,value", [
    ("email", "invalid-email"),
    ("phone", "123"),
    ("full_name", "Name123"),
    ("role", "UNKNOWN"),
])
def test_invalid_fields_and_roles_are_rejected(client, payload, field, value):
    payload[field] = value
    assert client.post("/auth/register", json=payload).status_code == 422


def test_supplier_registration_and_duplicate_phone(client, payload):
    payload["role"] = "SUPPLIER_ADMIN"
    payload["phone"] = "+91" + str(uuid4().int % 10**10).zfill(10)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    assert response.json()["role"] == "SUPPLIER_ADMIN"
    payload["email"] = uuid4().hex + "@example.com"
    assert client.post("/auth/register", json=payload).status_code == 409


def test_other_roles_can_be_selected(client, payload):
    for role in ["RESTAURANT_STAFF", "SUPPLIER_STAFF", "DRIVER", "PLATFORM_ADMIN"]:
        payload["email"] = uuid4().hex + "@example.com"
        payload["role"] = role
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 201
        assert response.json()["role"] == role
        assert response.json()["status"] == "ACTIVE"
