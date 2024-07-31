from typing import Union, Dict

from pydantic import BaseModel, Field

from app.config import settings
from app.log import Log
from app.version import VERSION


class Request(BaseModel):
    prompt: str


class APIResponseModel(BaseModel):
    code: int = Field(default=int(f"{settings.SERVICE_CODE}200"))
    message: str = Field(default=f"답변 성공 ({VERSION})" if Log.is_debug_enable() else "답변 성공")
    result: Union[str, Dict[str, Union[str, Dict[str, str]]]] = Field(default={})
    description: str = Field(default="답변 성공")
