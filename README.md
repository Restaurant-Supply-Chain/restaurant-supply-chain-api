# Restaurant Supply Chain API

A practice backend for managing the restaurant supply chain.

**Python 3.11+ · FastAPI · MySQL 8 · SQLAlchemy · Alembic · JWT**

## Quick start

Run these commands from the repository root in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Copy `.env.example` only on first setup. Edit `.env` with your database
password and a random `JWT_SECRET_KEY`. For Docker, use `DB_HOST=localhost`
and `DB_USER=root`. If port 3306 is occupied, set `DB_PORT=3307`.

Start Docker Desktop, then run:

```powershell
docker compose up -d db
# Wait for MySQL to be ready before applying migrations.
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Open **[Swagger UI](http://127.0.0.1:8000/docs)** to try the API.

## Available endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Create an active account |

### 1. Register

Choose any of the six roles from the role dropdown in Swagger. The default
is `RESTAURANT_ADMIN`. New accounts are active immediately.

```json
{
  "full_name": "Dev One",
  "email": "dev.one@example.com",
  "password": "Practice123!",
  "role": "RESTAURANT_ADMIN"
}
```

`phone` is optional. Email is normalized to lowercase. Passwords require
at least eight characters, uppercase and lowercase letters, a digit, and
a special character, with a maximum of 72 UTF-8 bytes for bcrypt.

## Tests

With MySQL running and migrations applied:

```powershell
python -m pytest app/tests -q
```

Tests roll back their database changes. Passwords are stored as bcrypt
hashes. HTTP and validation
errors use `application/problem+json`.

## Useful commands

| Task | Command |
|---|---|
| Apply migrations | `python -m alembic upgrade head` |
| Create a migration | `python -m alembic revision --autogenerate -m "describe change"` |
| Check schema changes | `python -m alembic check` |
| Stop MySQL and keep data | `docker compose stop db` |

Import new models in `app/models/__init__.py` and review generated
migrations before applying them. `.env`, `.venv`, and local admin
credentials are ignored by Git.

## Coming next

Login, refresh rotation, logout, current-user profile, password reset, RBAC, audit logs,
notifications, and authentication rate limiting.
