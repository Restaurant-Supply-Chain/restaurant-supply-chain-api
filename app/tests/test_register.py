from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.db.session import engine, get_db
from app.main import app
from app.models.user import User


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    # Savepoints let the endpoint commit while the test still rolls back its data.
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db):
    def test_db():
        yield db

    app.dependency_overrides[get_db] = test_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


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
    assert result["status"] == "PENDING"
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
    ("role", "PLATFORM_ADMIN"),
    ("role", "RESTAURANT_STAFF"),
    ("role", "SUPPLIER_STAFF"),
    ("role", "DRIVER"),
])
def test_invalid_fields_and_privileged_roles_are_rejected(client, payload, field, value):
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


def test_registration_is_documented():
    schema = app.openapi()
    assert "post" in schema["paths"]["/auth/register"]
    assert "/health" not in schema["paths"]
