import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.auth_rate_limit import AuthRateLimitMiddleware


@pytest.fixture
def limited_client():
    # Test routes exist only in this test app.
    test_app = FastAPI()
    test_app.add_middleware(AuthRateLimitMiddleware)

    @test_app.get("/auth/first")
    @test_app.get("/auth/second")
    @test_app.get("/public")
    def example():
        return {"ok": True}

    with TestClient(test_app) as client:
        yield client


def test_ten_requests_are_allowed_across_auth_routes(limited_client, monkeypatch):
    monkeypatch.setattr("app.middleware.auth_rate_limit.monotonic", lambda: 100.0)
    for number in range(10):
        path = "/auth/first" if number % 2 == 0 else "/auth/second"
        assert limited_client.get(path).status_code == 200
    blocked = limited_client.get("/auth/first")
    assert blocked.status_code == 429
    assert blocked.headers["content-type"] == "application/problem+json"
    assert blocked.headers["retry-after"] == "60"
    assert blocked.json()["status"] == 429 and blocked.json()["instance"] == "/auth/first"


def test_requests_are_allowed_after_the_window_expires(limited_client, monkeypatch):
    clock = [100.0]
    monkeypatch.setattr("app.middleware.auth_rate_limit.monotonic", lambda: clock[0])
    for _ in range(10):
        assert limited_client.get("/auth/first").status_code == 200
    clock[0] = 159.0
    blocked = limited_client.get("/auth/first")
    assert blocked.status_code == 429 and blocked.headers["retry-after"] == "1"
    clock[0] = 160.0
    assert limited_client.get("/auth/first").status_code == 200


def test_public_routes_are_not_limited(limited_client):
    for _ in range(15):
        assert limited_client.get("/public").status_code == 200
    for _ in range(10):
        assert limited_client.get("/auth/first").status_code == 200


def test_forwarded_headers_cannot_bypass_the_limit(limited_client):
    for number in range(10):
        assert limited_client.get("/auth/first", headers={
            "X-Forwarded-For": f"10.0.0.{number}",
        }).status_code == 200
    assert limited_client.get("/auth/first", headers={"X-Forwarded-For": "192.0.2.1"}).status_code == 429
