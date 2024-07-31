from typing import Annotated

from fastapi import APIRouter, Depends, Body
from fastapi.responses import JSONResponse

from app.dependencies import get_token_header
from app.docs.prompt import default_prompt_examples
from app.models import APIResponseModel, Request
from app.src.prompt.cot import cot_prompt
from app.src.prompt.deafult import default_prompt

router = APIRouter(
    prefix="/prompt",
    tags=["prompt"],
    dependencies=[Depends(get_token_header)],
)


@router.post("", response_model=APIResponseModel, response_class=JSONResponse)
async def default(
        request: Annotated[Request, Body(
            title="default prompting",
            description="기본 프롬프트 기법으로 답변 반환 API",
            media_type="application/json",
            openapi_examples=default_prompt_examples,
        )]
):
    result = default_prompt(request)
    return APIResponseModel(result=result, description="기본 프롬프트 기법으로 답변 성공")


@router.post("", response_model=APIResponseModel, response_class=JSONResponse)
async def cot(
        request: Annotated[Request, Body(
            title="CoT prompting",
            description="CoT 프롬프트 기법으로 답변 반환 API",
            media_type="application/json",
            openapi_examples=default_prompt_examples,
        )]
):
    result = cot_prompt(request)
    return APIResponseModel(result=result, description="CoT 프롬프트 기법으로 답변 성공")
