from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# from app.core.config import settings
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# DATABASE_URL = (
#     f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
#     f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
# )

# engine = create_engine(
#     DATABASE_URL,
#     pool_pre_ping=True,
# )

# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine,
# )


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    APP_NAME: str = "RSC-API"
    DEBUG: bool = True

    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "rsc_db"

    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

