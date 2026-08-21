from datetime import date
from decimal import Decimal

from app.extensions import db
from app.models import Category, Transaction


def find_category_id(app, name, kind):
    with app.app_context():
        category_id = db.session.scalar(
            db.select(Category.id).where(
                Category.name == name,
                Category.kind == kind,
            )
        )

        assert category_id is not None
        return category_id


def create_transaction(
    client,
    category_id,
    kind="expense",
    amount="25.50",
    description="Test groceries",
):
    return client.post(
        "/transactions/add",
        data={
            "kind": kind,
            "category_id": category_id,
            "amount": amount,
            "description": description,
            "transaction_date": date.today().isoformat(),
        },
    )


def test_user_can_create_transaction(client, app, auth):
    auth.register()

    food_id = find_category_id(app, "Food", "expense")
    response = create_transaction(client, food_id)

    assert response.status_code == 302

    with app.app_context():
        transaction = db.session.scalar(
            db.select(Transaction).where(
                Transaction.description == "Test groceries"
            )
        )

        assert transaction is not None
        assert transaction.amount == Decimal("25.50")
        assert transaction.transaction_date == date.today()
        assert transaction.category_id == food_id


def test_category_must_match_transaction_type(
    client,
    app,
    auth,
):
    auth.register()

    salary_id = find_category_id(app, "Salary", "income")

    response = create_transaction(
        client,
        salary_id,
        kind="expense",
    )

    assert response.status_code == 200

    with app.app_context():
        transaction_count = len(
            db.session.scalars(
                db.select(Transaction)
            ).all()
        )

        assert transaction_count == 0


def test_user_can_edit_and_delete_transaction(
    client,
    app,
    auth,
):
    auth.register()

    food_id = find_category_id(app, "Food", "expense")
    transport_id = find_category_id(
        app,
        "Transport",
        "expense",
    )

    create_transaction(client, food_id)

    with app.app_context():
        transaction_id = db.session.scalar(
            db.select(Transaction.id)
        )

    edit_response = client.post(
        f"/transactions/{transaction_id}/edit",
        data={
            "kind": "expense",
            "category_id": transport_id,
            "amount": "40.75",
            "description": "Updated transport cost",
            "transaction_date": date.today().isoformat(),
        },
    )

    assert edit_response.status_code == 302

    with app.app_context():
        transaction = db.session.get(
            Transaction,
            transaction_id,
        )

        assert transaction is not None
        assert transaction.amount == Decimal("40.75")
        assert transaction.description == "Updated transport cost"
        assert transaction.category_id == transport_id

    delete_response = client.post(
        f"/transactions/{transaction_id}/delete"
    )

    assert delete_response.status_code == 302

    with app.app_context():
        assert (
            db.session.get(Transaction, transaction_id)
            is None
        )


def test_user_can_create_edit_and_delete_category(
    client,
    app,
    auth,
):
    auth.register()

    create_response = client.post(
        "/transactions/categories",
        data={
            "name": "Subscriptions",
            "kind": "expense",
        },
    )

    assert create_response.status_code == 302

    with app.app_context():
        category_id = db.session.scalar(
            db.select(Category.id).where(
                Category.name == "Subscriptions"
            )
        )

        assert category_id is not None

    edit_response = client.post(
        f"/transactions/categories/{category_id}/edit",
        data={
            "name": "Digital Subscriptions",
            "kind": "expense",
        },
    )

    assert edit_response.status_code == 302

    with app.app_context():
        category = db.session.get(Category, category_id)

        assert category is not None
        assert category.name == "Digital Subscriptions"

    delete_response = client.post(
        f"/transactions/categories/{category_id}/delete"
    )

    assert delete_response.status_code == 302

    with app.app_context():
        assert db.session.get(Category, category_id) is None


def test_user_cannot_access_another_users_data(
    client,
    app,
    auth,
):
    auth.register()

    food_id = find_category_id(app, "Food", "expense")
    create_transaction(client, food_id)

    with app.app_context():
        transaction_id = db.session.scalar(
            db.select(Transaction.id)
        )

    auth.logout()

    auth.register(
        name="Second User",
        email="second@example.com",
        password="SecondPass123!",
    )

    transaction_edit_response = client.get(
        f"/transactions/{transaction_id}/edit"
    )
    transaction_delete_response = client.post(
        f"/transactions/{transaction_id}/delete"
    )
    category_edit_response = client.get(
        f"/transactions/categories/{food_id}/edit"
    )
    category_delete_response = client.post(
        f"/transactions/categories/{food_id}/delete"
    )

    assert transaction_edit_response.status_code == 404
    assert transaction_delete_response.status_code == 404
    assert category_edit_response.status_code == 404
    assert category_delete_response.status_code == 404

    with app.app_context():
        assert (
            db.session.get(Transaction, transaction_id)
            is not None
        )
        assert db.session.get(Category, food_id) is not None