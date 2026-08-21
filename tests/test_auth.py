from app.extensions import db
from app.models import User


def test_registration_creates_user_and_categories(
    client,
    app,
    auth,
):
    response = auth.register()

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert "_user_id" in session

    with app.app_context():
        user = db.session.scalar(
            db.select(User).where(
                User.email == "test@example.com"
            )
        )

        assert user is not None
        assert user.name == "Test User"
        assert user.password_hash != "TestPass123!"
        assert user.check_password("TestPass123!")
        assert len(user.categories) == 13


def test_duplicate_email_is_rejected(app, auth):
    auth.register()
    auth.logout()

    response = auth.register(name="Another User")

    assert response.status_code == 200

    with app.app_context():
        users = db.session.scalars(
            db.select(User).where(
                User.email == "test@example.com"
            )
        ).all()

        assert len(users) == 1


def test_user_can_log_in(client, auth):
    auth.register()
    auth.logout()

    with client.session_transaction() as session:
        assert "_user_id" not in session

    response = auth.login()

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert "_user_id" in session


def test_invalid_password_is_rejected(client, auth):
    auth.register()
    auth.logout()

    response = auth.login(password="WrongPass123!")

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "_user_id" not in session


def test_user_can_log_out(client, auth):
    auth.register()

    with client.session_transaction() as session:
        assert "_user_id" in session

    response = auth.logout()

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert "_user_id" not in session

    get_response = client.get("/auth/logout")
    assert get_response.status_code == 405