from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app


def test_unexpected_errors_return_safe_problem_details():
    def failing_db():
        raise RuntimeError("Private diagnostic details")

    previous = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = failing_db
    app.state.auth_requests = {}
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.post("/auth/login", json={
                "email": "review@example.com", "password": "Practice123!",
            })
        assert response.status_code == 500
        assert response.headers["content-type"] == "application/problem+json"
        assert response.json()["title"] == "Internal Server Error"
        assert response.json()["status"] == 500
        assert response.json()["instance"] == "/auth/login"
        assert "Private diagnostic details" not in response.text
        assert "Traceback" not in response.text
    finally:
        if previous is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous
        app.state.auth_requests = {}


def test_swagger_documents_actual_problem_responses():
    expected = {
        "/auth/register": ("post", [409, 422]),
        "/auth/login": ("post", [401, 403, 422]),
        "/auth/refresh": ("post", [401, 403, 422]),
        "/auth/logout": ("post", [401, 422]),
        "/auth/me": ("get", [401, 403]),
        "/auth/forgot-password": ("post", [422, 503]),
        "/auth/reset-password": ("post", [400, 422]),
    }
    paths = app.openapi()["paths"]
    for path, (method, codes) in expected.items():
        responses = paths[path][method]["responses"]
        for code in codes + [429, 500]:
            content = responses[str(code)]["content"]
            assert set(content) == {"application/problem+json"}
            schema = content["application/problem+json"]["schema"]
            assert {"title", "status", "detail", "instance"} <= set(schema["required"])
