from fastapi.testclient import TestClient
from auto_alpha_miner.dashboard.app import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
