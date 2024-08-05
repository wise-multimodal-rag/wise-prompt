from typing import Union, Dict, List, Any

from pydantic import BaseModel, Field

from app.config import settings
from app.constants import ModelOption, PromptTemplate
from app.log import Log
from app.version import VERSION


class LLMProviderRequest(BaseModel):
    llm_tool: str = Field(title="LLM 생성에 사용할 툴", description="Ollama, OpenAI 중 선택 가능", default="Ollama")
    model: str = Field(
        title="사용할 모델명",
        description="OpenAI 모델 잘못 설정할 경우, 과금이 큰 gpt-3.5-turbo 모델로 답변 생성하니 주의바람", default="llama3")
    temperature: float = Field(
        title="Model Output Randomness",
        description="0에 가까울수록 같은 결과를 내고 1이나 그 이상이면 더 다양한 단어(토큰)들을 뱉게 됨",
        default=ModelOption.TEMPERATURE)
    top_k: int = Field(description="LLM이 다음 단어(토큰)을 예측할 때 가장 확률 높은 k개 중 하나를 선택", default=ModelOption.TOP_K)


class Request(BaseModel):
    # TODO: 설명 or reasoning chain 필요한지 옵션
    system_prompt: str = Field(title="System Prompt", default=PromptTemplate.SYSTEM_PROMPT)
    prompt: str
    llm_provider: LLMProviderRequest = Field(default=LLMProviderRequest())


class AutoCoTRequest(Request):
    domain: str = Field(
        title="CoT 샘플로 사용할 도메인 설정",
        description="현재 사용 가능한 도메인: addsub, aqua, coin_flip, commonsensqa, date understanding, gsm8k, "
                    "last letters, multiarith, shuffled objects, singleeq, strategyqa, svamp\n"
                    "영어 문서로 해당 사이트 참고: https://github.com/kojima-takeshi188/zero_shot_cot/tree/main/log",
        default="multiarith")
    encoder_model: str = Field(
        description="which sentence-transformer encoder for clustering", default="all-MiniLM-L6-v2")
    n_clusters: int = Field(
        title="클러스터 개수", description="도메인 태스크에 따라 클러스터링 개수를 알맞게 설정해야함", default=8)
    cluster_random_seed: int = Field(title="랜덤 시드", default=192)
    max_ra_len: int = Field(title="Reasoning Chain 최대 길이", default=5)


class SelfConsistencyRequest(Request):
    num: int = Field(title="답변 생성 수행 횟수", description="비용 및 시간 주의해서 설정해야함", default=7)


class APIResponseModel(BaseModel):
    code: int = Field(default=int(f"{settings.SERVICE_CODE}200"))
    message: str = Field(default=f"답변 성공 ({VERSION})" if Log.is_debug_enable() else "답변 성공")
    result: Union[str, List[Union[str, Dict[str, Any]]], Dict[str, Union[str, Dict[str, str]]]] = Field(default={})
    description: str = Field(default="답변 성공")
