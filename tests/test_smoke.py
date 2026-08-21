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

def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}

def test_dark_mode_assets_are_available(client):
    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'data-theme="light"' in html
    assert 'id="theme-toggle"' in html
    assert "/static/css/theme.css" in html
    assert "/static/js/theme.js" in html

    css_response = client.get("/static/css/theme.css")
    javascript_response = client.get("/static/js/theme.js")

    assert css_response.status_code == 200
    assert javascript_response.status_code == 200