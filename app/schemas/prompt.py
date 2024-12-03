from typing import Dict, List

from pydantic import BaseModel, Field, field_validator

from app.constants import ModelOption, PromptTemplate
from app.exceptions.service import InvalidReActToolError


class LLMProviderRequest(BaseModel):
    llm_tool: str = Field(title="LLM 생성에 사용할 툴", description="Ollama, OpenAI 중 선택 가능", default="Ollama")
    model: str = Field(
        title="사용할 모델명", description="실제로 존재하는 모델명으로 설정해야함", default="llama3")
    temperature: float = Field(
        title="Model Output Randomness",
        description="0에 가까울수록 같은 결과를 내고 1이나 그 이상이면 더 다양한 단어(토큰)들을 뱉게 됨",
        default=ModelOption.TEMPERATURE)


class Request(BaseModel):
    # TODO: 설명 or reasoning chain 필요한지 옵션
    system_prompt: str = Field(title="System Prompt", default=PromptTemplate.SYSTEM_PROMPT)
    prompt: str = Field(title="프롬프트")
    llm_provider: LLMProviderRequest = Field(default=LLMProviderRequest())

    @field_validator('prompt')
    def check_prompt(cls, v):
        return v.strip()


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


class ReActRequest(Request):
    tool: str = Field(
        title="검색 툴 선택", description="Wikipedia, DuckDuckGoSearch 중에서 선택해서 사용 가능", default="Wikipedia")
    top_k_search_result: int = Field(title="상위 k개의 검색 결과", default=2)
    max_iterations: int = Field(
        title="실행을 종료하기 전에 수행할 최대 단계 수",
        description="""OpenAI의 경우, 호출 수가 많을 경우 과금의 우려가 있으나 주의바람. 
        또한 호출 수가 적을 경우, 답변이 누락될 수 있음 (`Agent stopped due to iteration limit or time limit.`)""",
        default=15)

    @field_validator('tool')
    def check_tool(cls, v: str):
        if v.lower() not in ['wikipedia', 'duckduckgosearch']:
            raise InvalidReActToolError(v)
        return v


class ReActResponse(BaseModel):
    answer: str = Field(title="답변")
    intermediate_steps: List[Dict[str, str]] = Field(title="", description="")


