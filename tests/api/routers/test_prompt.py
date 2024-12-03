import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

client = TestClient(app)


def common_router_test(response):
    assert response.status_code == 200
    response_json = response.json()
    print(response_json)
    assert list(response_json.keys()) == ["code", "message", "result", "description"]
    assert response_json["code"] == int(f"{settings.SERVICE_CODE}200")


@pytest.mark.skip(reason="로컬에서만 테스트 수행")
def test_default_prompt(request_body):
    response = client.post(url=f"/prompt", headers={"x-token": settings.X_TOKEN}, json=request_body)
    common_router_test(response)


@pytest.mark.skip(reason="로컬에서만 테스트 수행")
def test_cot_prompt(request_body):
    response = client.post(url=f"/prompt/cot", headers={"x-token": settings.X_TOKEN}, json=request_body)
    common_router_test(response)


@pytest.mark.skip(reason="로컬에서만 테스트 수행")
def test_auto_cot_prompt(request_body):
    response = client.post(url=f"/prompt/cot/auto", headers={"x-token": settings.X_TOKEN}, json=request_body)
    common_router_test(response)


@pytest.mark.skip(reason="로컬에서만 테스트 수행")
def test_self_consistency_prompt(request_body):
    response = client.post(url=f"/prompt/self-consistency", headers={"x-token": settings.X_TOKEN}, json=request_body)
    common_router_test(response)


@pytest.mark.skip(reason="유료 검색 API 필요함")
def test_react_prompt(request_body):
    response = client.post(url=f"/prompt/react", headers={"x-token": settings.X_TOKEN}, json=request_body)
    common_router_test(response)
