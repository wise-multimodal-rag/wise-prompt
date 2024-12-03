from typing import List

from pydantic import BaseModel, Field


class ApeInputOutput(BaseModel):
    inputs: List[str]
    outputs: List[str]


class ApeRequest(BaseModel):
    prompt_gen_data: ApeInputOutput = Field(description="LLM의 input, output은 내용과 개수가 일치해야함")
    eval_data: ApeInputOutput = Field(description="LLM의 input, output은 내용과 개수가 일치해야함")
    prompt_gen_model: str = Field(description="프롬프트를 생성할 때 사용할 OpenAI 모델", default='gpt-4o-mini')
    eval_model: str = Field(description="생성한 프롬프트를 평가할 때 사용할 OpenAI 모델", default='gpt-4o-mini')
    num_prompts: int = Field(description="생성할 프롬프트 개수", gt=1, default=50)
    eval_rounds: int = Field(description="평가 라운드 개수", ge=1, default=3)
    prompt_gen_batch_size: int = Field(description="", gt=1, default=20)
    eval_batch_size: int = Field(description="", gt=1, default=50)


class ApeResponse(BaseModel):
    prompt: str
    score: float
