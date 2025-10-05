from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "healthy"


def test_404_includes_trace_id():
    r = client.get("/does-not-exist")
    assert r.status_code == 404
    body = r.json()
    assert "trace_id" in body


