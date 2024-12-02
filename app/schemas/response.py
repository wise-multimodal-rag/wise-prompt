from typing import Any

from pydantic import BaseModel, Field

from app.config import settings
from app.log import Log
from app.version import VERSION


class APIResponseModel(BaseModel):
    """기본 API 응답 포맷 by AIP Restful API 디자인 가이드"""
    code: int = Field(default=int(f"{settings.SERVICE_CODE}200"))  # 6자리 숫자 권장
    message: str = Field(
        default=f"API Response Success ({VERSION})" if Log.is_debug_enable() else "API Response Success")
    result: Any = Field(default={})  # API response result
    description: str = Field(default="응답과 관련된 자세한 설명 작성")

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "result": self.result,
            "description": self.description
        }
