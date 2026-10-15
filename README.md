# Restaurant Supply Chain API

A team practice project connecting restaurants, suppliers, and delivery staff.

**Python 3.11+ · FastAPI · MySQL 8 · SQLAlchemy · Alembic · JWT**

## Dev1 module at a glance

**Owner:** [Viswa Chitturi](https://github.com/ViswaChitturi) · **Branch:** `feat/dev1-auth`
**Issue:** [#1 — Auth, Users, RBAC, Audit Logs, Notifications](https://github.com/Restaurant-Supply-Chain/restaurant-supply-chain-api/issues/1)

| Area | Implemented |
|---|---|
| Authentication | Signup, login, refresh rotation, logout, current profile, password reset |
| Access control | Six roles and the reusable `require_role(...)` dependency |
| Security | bcrypt passwords, hashed refresh tokens and OTPs, login lockout |
| Database | All nine Dev1 tables and Alembic migrations |
| Events | Auth audit records and stored in-app notifications |
| API behaviour | Auth rate limiting and RFC 7807 error responses |

This README covers the current Dev1 module. Other business modules are added by their owners.

## Quick start

Install **Python 3.11+** and **Docker Desktop**. Run these commands from the
repository root in Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Copy `.env.example` only on first setup. In `.env`, set your database password
and a random `JWT_SECRET_KEY`. For Docker, use `DB_HOST=localhost` and
`DB_USER=root`. If port 3306 is occupied, use `DB_PORT=3307`.

Start Docker Desktop, then run:

```powershell
docker compose up -d db
# Wait until MySQL reports that it is ready for connections.
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

**Open [Swagger UI](http://127.0.0.1:8000/docs)** to try the API.

## API guide

| Method | Endpoint | Request | Success |
|---|---|---|---|
| POST | `/auth/register` | Name, email, password, role; optional phone | 201: user profile |
| POST | `/auth/login` | Email and password | 200: token pair |
| POST | `/auth/refresh` | `refresh_token` | 200: new token pair |
| POST | `/auth/logout` | `refresh_token` | 204: no body |
| GET | `/auth/me` | Bearer access token | 200: current profile |
| POST | `/auth/forgot-password` | Email | 200: generic message |
| POST | `/auth/reset-password` | Email, OTP, new password | 200: confirmation |

### Register and log in

Use **Try it out** in Swagger with this signup example:

```json
{
  "full_name": "Dev One",
  "email": "dev.one@example.com",
  "password": "Practice123!",
  "role": "RESTAURANT_ADMIN"
}
```

All six roles are selectable: `PLATFORM_ADMIN`, `RESTAURANT_ADMIN`,
`RESTAURANT_STAFF`, `SUPPLIER_ADMIN`, `SUPPLIER_STAFF`, and `DRIVER`.
For this practice project, signup activates the account immediately. If omitted,
the role defaults to `RESTAURANT_ADMIN`.

Log in using the same email and password. Copy the returned access token,
click **Authorize**, and paste only the token value to try `/auth/me`.
Other clients send `Authorization: Bearer <access_token>`.

### Refresh and log out

Send your current refresh token to `/auth/refresh`. Save the new token pair;
the old refresh token is revoked and cannot be reused.

Send the newest refresh token to `/auth/logout` to revoke that session.
Repeating logout succeeds while the token is unexpired. Other sessions are
unaffected. Discard both tokens after logout; access tokens expire naturally.

### Reset a password

1. Call `/auth/forgot-password` with your email.
2. Read the six-digit OTP from the **Uvicorn terminal**.
3. Call `/auth/reset-password` with:

```json
{
  "email": "dev.one@example.com",
  "otp": "paste-the-six-digit-otp",
  "new_password": "Changed123!"
}
```

Replace the OTP placeholder with the actual six digits. OTPs last **15 minutes**
and work once; a new request invalidates older OTPs. Resetting a password clears
its login lock and revokes existing refresh tokens. Existing access tokens can
remain valid until expiry.

OTP console delivery requires `DEBUG=True`. Email/SMS delivery is not configured;
with debug disabled, forgot-password returns 503. API errors always stay in
problem format, including when local OTP debugging is enabled.

## Rules and errors

| Rule | Behaviour |
|---|---|
| Email | Validated, lowercase-normalized, unique; maximum 254 characters |
| Password | 8+ characters; uppercase, lowercase, digit, special character; at most 72 UTF-8 bytes |
| Tokens | Access: 15 minutes; refresh: 7 days with rotation |
| Login lock | Five failed attempts lock the account for 15 minutes |
| Auth rate limit | 10 requests per rolling minute per client IP across `/auth/*` |

The rate limiter uses memory in one API process. A 429 response includes
`Retry-After`; wait that many seconds before retrying. `LOGIN_MAX_ATTEMPTS`
and `LOGIN_LOCK_MINUTES` can be set in `.env`.

Errors use **`application/problem+json`** and are documented in Swagger:

```json
{
  "type": "about:blank",
  "title": "Bad Request",
  "status": 400,
  "detail": "Invalid or expired OTP.",
  "instance": "/auth/reset-password"
}
```

Validation errors also include an `errors` list. Unexpected failures return a
safe 500 response; diagnostic details appear only in the server console.

## For other backend developers

- Use `get_db` from `app.db.session` for database sessions.
- Use `get_current_user` from `app.core.deps` for authenticated routes.
- Use `require_role(...)` to restrict a route, listing its allowed roles explicitly:

```python
from fastapi import Depends
from app.core.constants import UserRole
from app.core.deps import require_role

@router.get("/example")
def example(user=Depends(require_role(UserRole.PLATFORM_ADMIN))):
    return {"user_id": user.id}
```

Role checks use the current `users.role`. The `roles` table contains all six
roles; `permissions`, `user_roles`, and `role_permissions` provide the schema
for additional permission mapping and are not currently used by the role check.

Use `record_audit` from `app.services.audit` and `create_notification` from
`app.services.notification` for events. These helpers add records to the session;
the calling service commits them with its business changes. Never include
passwords, OTPs, or tokens in audit snapshots or notification payloads.

Notifications are stored as in-app messages for signup, lockout, and password
changes. Audit/inbox query routes and external notification delivery are outside
the current issue's endpoint list.

## Database and tests

Dev1 tables: `users`, `roles`, `permissions`, `user_roles`, `role_permissions`,
`refresh_tokens`, `password_resets`, `audit_logs`, and `notifications`.
Datetimes are stored in UTC. MySQL data is kept in a Docker volume.

With MySQL running and migrations applied:

```powershell
python -m pytest app/tests -q
```

Tests cover authentication, rotation, reset, RBAC, event records, rate limits,
and error contracts. Their database changes are rolled back.

| Task | Command |
|---|---|
| Apply migrations | `python -m alembic upgrade head` |
| Create a migration | `python -m alembic revision --autogenerate -m "describe change"` |
| Check schema changes | `python -m alembic check` |
| Stop MySQL and keep data | `docker compose stop db` |

Import new models in `app/models/__init__.py` and review migrations before
applying them. `.env`, `.venv`, and local credentials are ignored by Git.

## Handoff status

Core issue features are implemented locally. Remaining handoff steps:

- Manual Swagger verification of all seven endpoints.
- Push the completed feature commits to `feat/dev1-auth`.
- PR review and merge into `main`, with `Closes #1` in the PR description.

Broader project work still includes a Postman collection, API Dockerfile,
shared project documentation, and the general 100 requests/minute/user limit
for other modules. These are separate from the implemented auth IP limit.
