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


def test_openapi_json():
    response = client.get("/openapi.json")
    print(response)
    import json
    import pathlib
    p = pathlib.Path('./openapi.json')
    p.write_text(json.dumps(response.json(), ensure_ascii=False), encoding='utf8')
