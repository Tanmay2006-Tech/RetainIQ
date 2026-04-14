from fastapi.testclient import TestClient

from backend.app.main import app


def test_predict_endpoint_contract() -> None:
    client = TestClient(app)

    payload = {
        "age": 39,
        "monthly_spend": 91,
        "tenure_months": 11,
        "support_tickets_90d": 4,
        "login_days_30d": 8,
        "contract_type": "month-to-month",
        "payment_method": "electronic-check",
        "region": "north",
    }
    login = client.post(
        "/auth/login",
        json={"username": "admin", "password": "churn123"},
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.post("/predict", json=payload, headers=headers)
    assert response.status_code == 200

    body = response.json()
    assert "churn_probability" in body
    assert "risk_category" in body
    assert "explanation" in body
    assert "recommendations" in body


def test_login_and_revenue_endpoints() -> None:
    client = TestClient(app)

    login = client.post(
        "/auth/login",
        json={"username": "admin", "password": "churn123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    revenue = client.get("/revenue-impact", headers=headers)
    assert revenue.status_code == 200
    body = revenue.json()
    assert "total_risk_revenue" in body
    assert "top_customers" in body
