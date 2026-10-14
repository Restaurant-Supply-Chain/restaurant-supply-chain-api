import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException

from app.core.constants import UserRole, UserStatus
from app.core.deps import require_role
from app.core.exceptions import http_exception_handler
from app.db.session import get_db
from app.models.rbac import Permission, Role, RolePermission, UserRoleAssignment


@pytest.fixture
def role_client(db):
    # These protected routes exist only in the test app, not in the project API.
    test_app = FastAPI()
    test_app.add_exception_handler(HTTPException, http_exception_handler)
    test_app.dependency_overrides[get_db] = lambda: db

    @test_app.get("/admin")
    def admin(user=Depends(require_role(UserRole.PLATFORM_ADMIN))):
        return {"role": user.role}

    @test_app.get("/operations")
    def operations(user=Depends(require_role(UserRole.RESTAURANT_STAFF, UserRole.DRIVER))):
        return {"role": user.role}

    with TestClient(test_app) as client:
        yield client


def test_role_checks_use_current_account_role(role_client, db, login_tokens):
    user, tokens = login_tokens
    headers = {"Authorization": "Bearer " + tokens["access_token"]}
    denied = role_client.get("/admin", headers=headers)
    assert denied.status_code == 403
    assert denied.headers["content-type"] == "application/problem+json"
    user.role = UserRole.PLATFORM_ADMIN
    db.commit()
    assert role_client.get("/admin", headers=headers).status_code == 200
    for role in [UserRole.RESTAURANT_STAFF, UserRole.DRIVER]:
        user.role = role
        db.commit()
        assert role_client.get("/operations", headers=headers).status_code == 200


def test_role_checks_require_authenticated_active_user(role_client, db, login_tokens):
    user, tokens = login_tokens
    assert role_client.get("/admin").status_code == 401
    refresh_headers = {"Authorization": "Bearer " + tokens["refresh_token"]}
    assert role_client.get("/admin", headers=refresh_headers).status_code == 401
    user.role = UserRole.PLATFORM_ADMIN
    user.status = UserStatus.SUSPENDED
    db.commit()
    headers = {"Authorization": "Bearer " + tokens["access_token"]}
    assert role_client.get("/admin", headers=headers).status_code == 403


def test_rbac_tables_store_links_and_prevent_duplicates(db, login_tokens):
    user, _ = login_tokens
    roles = db.query(Role).all()
    assert {role.name for role in roles} == {role.value for role in UserRole}
    role = db.query(Role).filter_by(name=user.role.value).one()
    permission = Permission(name="test:profile:read")
    db.add(permission)
    db.flush()
    db.add(UserRoleAssignment(user_id=user.id, role_id=role.id))
    db.add(RolePermission(role_id=role.id, permission_id=permission.id))
    db.flush()
    assert db.query(RolePermission).filter_by(role_id=role.id, permission_id=permission.id).count() == 1
    with pytest.raises(IntegrityError):
        with db.begin_nested():
            db.add(Permission(name=permission.name))
            db.flush()
