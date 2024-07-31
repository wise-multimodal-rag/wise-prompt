from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

client = TestClient(app)


def test_read_users():
    response = client.get("/users", headers={"x-token": settings.X_TOKEN})
    assert response.status_code == 200
    response_json = response.json()
    assert list(response_json.keys()) == ["code", "message", "result", "description"]
    assert response_json["code"] == int(f"{settings.SERVICE_CODE}200")


def test_read_user_me():
    response = client.get("/users/me", headers={"x-token": settings.X_TOKEN})
    assert response.status_code == 200
    response_json = response.json()
    assert list(response_json.keys()) == ["code", "message", "result", "description"]
    assert response_json["code"] == int(f"{settings.SERVICE_CODE}200")


def test_read_user():
    user_name = "sally"
    response = client.get(f"/users/{user_name}", headers={"x-token": settings.X_TOKEN})
    assert response.status_code == 200
    response_json = response.json()
    assert list(response_json.keys()) == ["code", "message", "result", "description"]
    assert response_json["code"] == int(f"{settings.SERVICE_CODE}200")
