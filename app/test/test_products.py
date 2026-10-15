from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_application_starts():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "Restaurant Supply Chain API" in response.json()["info"]["title"]


def test_products_endpoint_is_registered():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]

    assert "/api/v1/catalog/products" in paths
    assert "/api/v1/catalog/products/{product_id}" in paths


def test_products_rejects_invalid_limit():
    response = client.get(
        "/api/v1/catalog/products",
        params={"limit": 0},
    )

    assert response.status_code == 422


def test_products_rejects_negative_skip():
    response = client.get(
        "/api/v1/catalog/products",
        params={"skip": -1},
    )

    assert response.status_code == 422
