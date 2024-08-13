from typing import Annotated

from fastapi import APIRouter, Depends, Body
from fastapi.responses import JSONResponse

from app.dependencies import get_token_header
from app.docs.prompt import default_prompt_examples, self_consistency_examples, react_examples, auto_cot_examples
from app.models import APIResponseModel, Request, AutoCoTRequest, SelfConsistencyRequest, ReActRequest, ReActResponse
from app.src.prompt.auto_cot import auto_cot_prompt
from app.src.prompt.cot import cot_prompt
from app.src.prompt.default import default_prompt
from app.src.prompt.react import react_prompt
from app.src.prompt.self_consistency import self_consistency_prompt
from app.version import VERSION

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
            openapi_examples=default_prompt_examples,  # pyright: ignore
        )]
):
    """기본 프롬프트로 내장된 시스템 프롬프트를 기준으로 설정한 LLM이 답변을 생성합니다."""
    result = default_prompt(request.system_prompt, request.prompt, request.llm_provider)
    return APIResponseModel(result=result, description="기본 프롬프트 기법으로 답변 성공")


@router.post("/cot", response_model=APIResponseModel, response_class=JSONResponse)
async def cot(
        request: Annotated[Request, Body(
            title="CoT prompting",
            description="CoT 프롬프트 기법으로 답변 반환 API",
            media_type="application/json",
            openapi_examples=default_prompt_examples,  # pyright: ignore
        )]
):
    """원래의 프롬프트에 "단계별로 생각하기"라는 magic sentence를 추가하는 것"""
    result = cot_prompt(request.system_prompt, request.prompt, request.llm_provider)
    return APIResponseModel(result=result, description="CoT 프롬프트 기법으로 답변 성공")


@router.post("/cot/auto", response_model=APIResponseModel, response_class=JSONResponse)
async def auto_cot(
        request: Annotated[AutoCoTRequest, Body(
            title="Auto-CoT prompting",
            description="Auto-CoT 프롬프트 기법으로 답변 반환 API",
            media_type="application/json",
            openapi_examples=auto_cot_examples,  # pyright: ignore
        )]
):
    """Questions and reasoning chains automatically

    - 초기 sbert 모델이 로드될 때, 시간이 걸릴 수 있음\n
    - 현재 사용 가능한 도메인: _addsub, aqua, coin_flip, commonsensqa, date understanding, gsm8k, last letters, multiarith, shuffled objects, singleeq, strategyqa, svamp_ \n
        - 영어 문서로 해당 사이트 참고: https://github.com/kojima-takeshi188/zero_shot_cot/tree/main/log\n

    ### 방법론
    1. **Question Clustering**: 주어진 데이터 세트의 질문을 몇 개의 클러스터로 분할한다.\n
        1. 각 question에 대해 vector representation을 계산한다. (S-BERT)\n
        2. fix-sized question representation (avg.)\n
        3. k-means\n
        4. cluster의 center와 distance 차이로 sorting 한다.\n\n
    2. **Demonstration Sampling**: 각 클러스터에서 대표 질문을 선택하고, 간단한 heuristics과 함께 Zero-Shot-CoT를 사용해 reasoning chain을 생성한다.\n
        1. 각 cluster마다 demonstration을 구축한다.\n
        2. input은 Zero-shot-CoT에 fed한다.\n
        3. q에 대한 rationale r과 answer a를 생성한다.\n
        4. q, r이 selection criteria를 만족하면 demonstration set에 추가한다.
    """
    result = auto_cot_prompt(
        request.domain, request.system_prompt, request.prompt, request.llm_provider,
        request.encoder_model, request.n_clusters, request.cluster_random_seed, request.max_ra_len)
    return APIResponseModel(result=result, description="Auto-CoT 프롬프트 기법으로 답변 성공")


@router.post("/self-consistency", response_model=APIResponseModel, response_class=JSONResponse)
async def self_consistency(
        request: Annotated[SelfConsistencyRequest, Body(
            title="Self-consistency prompting",
            description="Self-consistency 프롬프트 기법으로 답변 반환 API",
            media_type="application/json",
            openapi_examples=self_consistency_examples,  # pyright: ignore
        )]
):
    """CoT(Chain-of-Thought)의 연장선으로 하나의 답변이 아니라 여러 개의 사고 과정을 생성하고 그 중 다수결로 최종 답변을 결정하는 방식

    ### 특징\n
    - 단답형이나 객관식만 사용 가능하다. (서술형 사용 불가)
    - OpenAI 모델을 사용해야 여러 번 응답 없이 적절한 답변이 나온다. (Ollama 모델로는 현재 제대로 답변 불가)
    """
    result = self_consistency_prompt(request.system_prompt, request.prompt, request.llm_provider, request.num)
    return APIResponseModel(result=result, description="Self-consistency 프롬프트 기법으로 답변 성공")


@router.post("/react", response_model=APIResponseModel, response_class=JSONResponse)
async def react(
        request: Annotated[ReActRequest, Body(
            title="ReAct prompting",
            description="ReAct 프롬프트 기법으로 답변 반환 API",
            media_type="application/json",
            openapi_examples=react_examples,  # pyright: ignore
        )]
):
    """추론(Reasoning)과 행동(Action)을 연결하여 문제를 해결하는 방식\n
    이는 모델이 문제에 대해 추론한 후, 그에 따른 행동을 생성하고, 다시 그 행동의 결과를 바탕으로 추론하는 과정을 반복하는 것을 의미합니다.

    - 해당 방법론은 `Wikipedia`, `DuckDuckGoSearch` 검색기를 통해서 정보를 얻어 최종결과를 생성합니다.\n
    - 현재 검색 결과를 기반으로 답변을 하는 방법론이기 때문에 검색이 제대로 되지 않았을 경우 답변을 제대로 하지 못할 수 있습니다.\n
    - 특정 모델과 검색기에 따라서 결과가 매우 달라질 수 있습니다.
    """
    answer, intermediate_steps = react_prompt(request.system_prompt, request.prompt, request.llm_provider,
                                              request.tool, request.top_k_search_result, request.max_iterations)
    result_ = ReActResponse(answer=answer, intermediate_steps=intermediate_steps)  # pyright: ignore
    if answer.strip() == "Agent stopped due to iteration limit or time limit.":
        return APIResponseModel(message=f"답변 실패 ({VERSION})", result=result_, description="ReAct 프롬프트 기법으로 답변 실패")
    else:
        return APIResponseModel(result=result_, description="ReAct 프롬프트 기법으로 답변 성공")
