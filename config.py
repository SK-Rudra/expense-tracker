import os


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1,
        )

    if database_url.startswith("postgresql://"):
        return database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    return database_url


def get_secret_key() -> str:
    secret_key = os.getenv("SECRET_KEY")

    if secret_key:
        return secret_key

    if os.getenv("APP_ENV", "development").lower() == "production":
        raise RuntimeError(
            "SECRET_KEY must be configured in production."
        )

    return "development-secret-key"


class Config:
    IS_PRODUCTION = (
        os.getenv("APP_ENV", "development").lower()
        == "production"
    )

    SECRET_KEY = get_secret_key()

    SQLALCHEMY_DATABASE_URI = normalize_database_url(
        os.getenv(
            "DATABASE_URL",
            "sqlite:///expense_tracker.db",
        )
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = IS_PRODUCTION

    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = IS_PRODUCTION