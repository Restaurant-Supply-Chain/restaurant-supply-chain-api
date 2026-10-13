import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import engine, get_db
from app.main import app


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

    app.dependency_overrides[get_db] = test_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
