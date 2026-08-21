import pytest

from config import get_secret_key, normalize_database_url


def test_sqlite_url_is_unchanged():
    database_url = "sqlite:///expense_tracker.db"

    assert normalize_database_url(database_url) == database_url


def test_postgresql_url_uses_psycopg():
    database_url = "postgresql://user:password@host/database"

    assert normalize_database_url(database_url) == (
        "postgresql+psycopg://user:password@host/database"
    )


def test_legacy_postgres_url_uses_psycopg():
    database_url = "postgres://user:password@host/database"

    assert normalize_database_url(database_url) == (
        "postgresql+psycopg://user:password@host/database"
    )


def test_production_requires_secret_key(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.raises(
        RuntimeError,
        match="SECRET_KEY must be configured",
    ):
        get_secret_key()