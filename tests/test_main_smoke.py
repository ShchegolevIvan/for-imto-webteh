from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_openapi_available():
    assert client.get("/openapi.json").status_code == 200

def test_metrics_available():
    assert client.get("/metrics").status_code == 200
