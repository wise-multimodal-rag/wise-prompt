from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

client = TestClient(app)


def test_read_items():
    response = client.get("/prompt", headers={"x-token": settings.X_TOKEN})
    assert response.status_code == 200
    response_json = response.json()
    assert list(response_json.keys()) == ["code", "message", "result", "description"]
    assert response_json["code"] == int(f"{settings.SERVICE_CODE}200")


def test_read_item():
    item_id = "gun"
    response = client.get(f"/prompt/{item_id}", headers={"x-token": settings.X_TOKEN})
    assert response.status_code == 200
    response_json = response.json()
    assert list(response_json.keys()) == ["code", "message", "result", "description"]
    assert response_json["code"] == int(f"{settings.SERVICE_CODE}200")


def test_update_item():
    item_id = "plumbus"
    response = client.put(f"/prompt/{item_id}", headers={"x-token": settings.X_TOKEN})
    assert response.status_code == 200
    response_json = response.json()
    assert list(response_json.keys()) == ["code", "message", "result", "description"]
    assert response_json["code"] == int(f"{settings.SERVICE_CODE}200")


def test_create_item():
    item = {
        "name": "apple",
        "status": "in stock",
        "stock": 10
    }
    response = client.post(url="/prompt", headers={"x-token": settings.X_TOKEN},
                           json=item)
    assert response.status_code == 200
    assert response.json()["result"]["item"]["name"] == item["name"]
    assert response.json()["result"]["item"]["status"] == item["status"]
    assert response.json()["result"]["item"]["stock"] == item["stock"]
