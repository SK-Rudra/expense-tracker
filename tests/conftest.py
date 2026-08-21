import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def app(tmp_path):
    database_path = tmp_path / "test_expense_tracker.db"

    test_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "testing-secret-key",
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": (
                f"sqlite:///{database_path.as_posix()}"
            ),
        }
    )

    with test_app.app_context():
        db.create_all()

    yield test_app

    with test_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

class AuthActions:
    def __init__(self, client):
        self.client = client

    def register(
        self,
        name="Test User",
        email="test@example.com",
        password="TestPass123!",
    ):
        return self.client.post(
            "/auth/register",
            data={
                "name": name,
                "email": email,
                "password": password,
                "confirm_password": password,
            },
        )

    def login(
        self,
        email="test@example.com",
        password="TestPass123!",
    ):
        return self.client.post(
            "/auth/login",
            data={
                "email": email,
                "password": password,
                "remember": False,
            },
        )

    def logout(self):
        return self.client.post("/auth/logout")


@pytest.fixture()
def auth(client):
    return AuthActions(client)