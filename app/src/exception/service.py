"""
서비스 자체 로직에 관한 커스텀 예외처리 작성
"""
import json

from starlette import status

from app.config import settings


class SampleServiceError(Exception):

    def __init__(self, code: int, message: str, result):
        self.code = code
        self.message = message
        self.result = result

    def __str__(self):
        exception_data = {
            "code": self.code,
            "message": self.message,
            "result": self.result
        }
        return json.dumps(exception_data, indent=4, ensure_ascii=False)


class TokenValidationError(SampleServiceError):
    """유효하지 않은 토큰 설정"""

    def __init__(self, x_token):
        self.code = int(f"{settings.SERVICE_CODE}{status.HTTP_401_UNAUTHORIZED}")
        self.message = "Invalid x-token header"
        self.result = {"current_x_token": x_token}


class InvalidItemStock(SampleServiceError):
    """유효하지 않은 아이템 재고값 설정"""

    def __init__(self, stock):
        self.code = int(f"{settings.SERVICE_CODE}{status.HTTP_400_BAD_REQUEST}")
        self.message = "Invalid stock"
        self.result = {"current_stock": stock}
