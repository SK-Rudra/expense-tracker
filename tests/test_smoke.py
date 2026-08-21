def test_home_page_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Expense Tracker" in response.data


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_transactions_require_login(client):
    response = client.get("/transactions/")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]