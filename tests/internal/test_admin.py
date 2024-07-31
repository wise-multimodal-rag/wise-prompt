from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

client = TestClient(app)


def test_update_admin():
    response = client.post(url="/admin", headers={"x-token": settings.X_TOKEN})
    assert response.status_code == 200
    response_json = response.json()
    assert list(response_json.keys()) == ["code", "message", "result", "description"]
    assert response_json["code"] == int(f"{settings.SERVICE_CODE}200")
