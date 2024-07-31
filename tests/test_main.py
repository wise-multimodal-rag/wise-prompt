from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/", headers={"x-token": settings.X_TOKEN})
    assert response.status_code == 200


def test_health():
    response = client.get("/health", headers={"x-token": settings.X_TOKEN})
    assert response.status_code == 200
