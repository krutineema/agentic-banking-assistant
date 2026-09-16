from fastapi.testclient import TestClient

from app.main import app


def test_protected_endpoint_requires_login():
    with TestClient(app) as client:
        response = client.get("/api/accounts")
        assert response.status_code == 401


def test_invalid_credentials_are_rejected():
    with TestClient(app) as client:
        response = client.post(
            "/api/auth/login",
            json={"username": "demo.alex", "password": "wrong"},
        )
        assert response.status_code == 401


def test_login_creates_customer_scoped_session():
    with TestClient(app) as client:
        login = client.post(
            "/api/auth/login",
            json={"username": "demo.sam", "password": "Banking456!"},
        )
        assert login.status_code == 200
        assert login.json()["customer_id"] == "cust-002"
        assert "northstar_session" in client.cookies

        accounts = client.get("/api/accounts")
        assert accounts.status_code == 200
        assert {a["customer_id"] for a in accounts.json()} == {"cust-002"}
        assert {a["id"] for a in accounts.json()} == {"acc-current-002", "acc-savings-002"}

        transactions = client.get("/api/transactions")
        assert transactions.status_code == 200
        assert {t["account_id"] for t in transactions.json()} <= {
            "acc-current-002",
            "acc-savings-002",
        }


def test_assistant_uses_authenticated_customer_scope():
    with TestClient(app) as alex_client, TestClient(app) as sam_client:
        alex_client.post(
            "/api/auth/login",
            json={"username": "demo.alex", "password": "Banking123!"},
        )
        sam_client.post(
            "/api/auth/login",
            json={"username": "demo.sam", "password": "Banking456!"},
        )

        alex = alex_client.post(
            "/api/assistant/message",
            json={"message": "How much did I spend eating out in August?"},
        )
        sam = sam_client.post(
            "/api/assistant/message",
            json={"message": "How much did I spend eating out in August?"},
        )

        assert alex.json()["data"]["total"] == "69.60"
        assert sam.json()["data"]["total"] == "25.00"


def test_logout_invalidates_session():
    with TestClient(app) as client:
        client.post(
            "/api/auth/login",
            json={"username": "demo.alex", "password": "Banking123!"},
        )
        logout = client.post("/api/auth/logout")
        assert logout.status_code == 204
        assert client.get("/api/accounts").status_code == 401
