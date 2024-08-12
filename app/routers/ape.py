from typing import Annotated

from fastapi import APIRouter, Depends, Body
from fastapi.responses import JSONResponse

from app.dependencies import get_token_header
from app.docs.ape import ape_examples
from app.models import APIResponseModel, ApeRequest
from app.src.ape.ape import ape

router = APIRouter(
    prefix="/ape",
    tags=["automatic-prompt-engineer"],
    dependencies=[Depends(get_token_header)],
)


@router.post("", response_model=APIResponseModel, response_class=JSONResponse)
async def automatic_prompt_engineer(
        request: Annotated[ApeRequest, Body(
            title="Automatic Prompt Engineer API",
            description="Automatic Prompt Engineer 방식으로 Few shot 데이터셋을 통한 Instruction 생성 및 평가 수항",
            media_type="application/json",
            openapi_examples=ape_examples,  # pyright: ignore
        )]
):
    """자동으로 Instruction을 생성하고 선택하는 방법론 (참고: [APE Github](https://github.com/keirp/automatic_prompt_engineer?tab=readme-ov-file))

    LLM으로 instruction candidate set을 생성하고, score function을 통한 filtering 과정을 거쳐 최적의 instruction을 선택함

    - **구성요소**
        - ***LLM as Inference Models***: LLM을 사용하여 태스크에 대한 명령어 후보 생성 ➡️ Initial Proposal Distributions
        - ***LLM as Scoring Models***: LLM을 사용하여 태스크에 대한 점수 생성 (UCB 알고리즘) ➡️ Score Function

    - **주의사항**
        - **호출 후 응답을 받기까지 오랜 시간이 걸리므로 주의바람**
        - **Automatic Prompt Engineering은 LLM 생성이 많이 필요한 방법론으로 OpenAI 과금을 고려해야함**
        - `eval_rounds`, `prompt_gen_batch_size`, `eval_batch_size` 등을 어떻게 설정하냐에 따라서 LLM 생성 횟수 달라짐
    """
    result = ape(request.prompt_gen_data, request.eval_data, request.prompt_gen_model, request.eval_model, request.num_prompts,
                 request.eval_rounds, request.prompt_gen_batch_size, request.eval_batch_size)
    return APIResponseModel(
        result=result, description="Automatic Prompt Engineer 방식으로 프롬프트 생성 및 평가 완료")  # pyright: ignore
