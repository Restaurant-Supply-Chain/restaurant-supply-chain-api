
from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import URL

from app.core.config import settings
from app.db.base import Base
from app.modules.products import models as product_models


# Alembic configuration
config = context.config

# Build the MySQL URL from settings in app/core/config.py
database_url = URL.create(
    drivername="mysql+pymysql",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
)

# Override the placeholder URL in alembic.ini
config.set_main_option(
    "sqlalchemy.url",
    database_url.render_as_string(hide_password=False).replace("%", "%%"),
)

# Metadata for detecting SQLAlchemy models
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Explicitly use the configured MySQL URL
    connectable = engine_from_config(
        {
            "sqlalchemy.url": config.get_main_option("sqlalchemy.url"),
        },
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()