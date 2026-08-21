import re
from datetime import date, timedelta

from app.extensions import db
from app.models import Category, User


def get_user_category_id(app, email, name, kind):
    with app.app_context():
        category_id = db.session.scalar(
            db.select(Category.id)
            .join(User, Category.user_id == User.id)
            .where(
                User.email == email,
                Category.name == name,
                Category.kind == kind,
            )
        )

        assert category_id is not None
        return category_id


def post_transaction(
    client,
    category_id,
    kind,
    amount,
    description,
    transaction_date,
):
    return client.post(
        "/transactions/add",
        data={
            "kind": kind,
            "category_id": category_id,
            "amount": amount,
            "description": description,
            "transaction_date": transaction_date.isoformat(),
        },
    )


def test_dashboard_calculates_current_month_totals(
    client,
    app,
    auth,
):
    auth.register()

    salary_id = get_user_category_id(
        app,
        "test@example.com",
        "Salary",
        "income",
    )
    food_id = get_user_category_id(
        app,
        "test@example.com",
        "Food",
        "expense",
    )

    today = date.today()
    previous_month_date = today.replace(day=1) - timedelta(days=1)

    post_transaction(
        client,
        salary_id,
        "income",
        "1000.00",
        "Current salary",
        today,
    )
    post_transaction(
        client,
        food_id,
        "expense",
        "250.00",
        "Current groceries",
        today,
    )
    post_transaction(
        client,
        food_id,
        "expense",
        "900.00",
        "Previous month expense",
        previous_month_date,
    )

    response = client.get("/dashboard")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "+$1,000.00" in html
    assert "-$250.00" in html
    assert "$750.00" in html
    assert "Current salary" in html
    assert "Current groceries" in html

    assert re.search(
        r"<h2>\s*2\s*</h2>\s*"
        r"<span>Recorded this month</span>",
        html,
    )


def test_dashboard_does_not_show_another_users_data(
    client,
    app,
    auth,
):
    auth.register()

    first_user_food_id = get_user_category_id(
        app,
        "test@example.com",
        "Food",
        "expense",
    )

    post_transaction(
        client,
        first_user_food_id,
        "expense",
        "400.00",
        "Private first user expense",
        date.today(),
    )

    auth.logout()

    auth.register(
        name="Second User",
        email="second@example.com",
        password="SecondPass123!",
    )

    second_user_salary_id = get_user_category_id(
        app,
        "second@example.com",
        "Salary",
        "income",
    )

    post_transaction(
        client,
        second_user_salary_id,
        "income",
        "100.00",
        "Second user income",
        date.today(),
    )

    response = client.get("/dashboard")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Second user income" in html
    assert "+$100.00" in html

    assert "Private first user expense" not in html
    assert "$400.00" not in html

def test_home_shows_logged_in_users_current_month_totals(
    client,
    app,
    auth,
):
    auth.register()

    salary_id = get_user_category_id(
        app,
        "test@example.com",
        "Salary",
        "income",
    )
    food_id = get_user_category_id(
        app,
        "test@example.com",
        "Food",
        "expense",
    )

    today = date.today()
    previous_month_date = today.replace(day=1) - timedelta(days=1)

    post_transaction(
        client,
        salary_id,
        "income",
        "1200.00",
        "Current income",
        today,
    )
    post_transaction(
        client,
        food_id,
        "expense",
        "325.00",
        "Current expense",
        today,
    )
    post_transaction(
        client,
        food_id,
        "expense",
        "999.00",
        "Previous expense",
        previous_month_date,
    )

    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert re.search(r"<h2>\s*\$875\.00\s*</h2>", html)
    assert re.search(
        r'class="income">\s*\$1,200\.00\s*</strong>',
        html,
    )
    assert re.search(
        r'class="expense">\s*\$325\.00\s*</strong>',
        html,
    )
    assert "$999.00" not in html