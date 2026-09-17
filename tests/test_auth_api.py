from fastapi.testclient import TestClient

from app.main import app


def test_protected_endpoint_requires_login():
    with TestClient(app) as client:
        assert client.get("/api/accounts").status_code == 401


def test_login_creates_customer_scoped_session():
    with TestClient(app) as client:
        login = client.post("/api/auth/login", json={"username": "demo.sam", "password": "Banking456!"})
        assert login.status_code == 200
        accounts = client.get("/api/accounts")
        assert {a["customer_id"] for a in accounts.json()} == {"cust-002"}


def test_assistant_reads_from_database_for_authenticated_customer():
    with TestClient(app) as client:
        client.post("/api/auth/login", json={"username": "demo.alex", "password": "Banking123!"})
        response = client.post("/api/assistant/message", json={"message": "How much did I spend eating out in August?"})
        assert response.status_code == 200
        assert response.json()["data"]["total"] == "69.60"


def test_health_reports_sqlite_stage():
    with TestClient(app) as client:
        payload = client.get("/health").json()
        assert payload["stage"] == "1B"
        assert payload["persistence"] == "sqlite"
