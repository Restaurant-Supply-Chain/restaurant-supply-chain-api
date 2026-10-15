from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import engine, get_db
from app.main import app
from app.models.user import User


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    # Savepoints allow commits inside an endpoint without keeping test data.
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

    # Each test gets a fresh rate-limit window; the limiter remains enabled.
    app.state.auth_requests = {}
    app.dependency_overrides[get_db] = test_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.state.auth_requests = {}

@pytest.fixture
def login_tokens(client, db):
    email = uuid4().hex + "@example.com"
    registered = client.post("/auth/register", json={
        "full_name": "Session Test", "email": email, "password": "Practice123!",
    })
    assert registered.status_code == 201
    user = db.get(User, registered.json()["id"])
    response = client.post("/auth/login", json={"email": email, "password": "Practice123!"})
    assert response.status_code == 200
    return user, response.json()
