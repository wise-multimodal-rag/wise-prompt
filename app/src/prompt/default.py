from app.models import LLMProviderRequest
from app.constants import PromptTemplate
from app.src.llm_provider.llm_tool import model_setting


def default_prompt(system_prompt, prompt, llm_provider: LLMProviderRequest):
    model = model_setting(llm_provider.llm_tool, llm_provider.model, llm_provider.temperature)
    chain = PromptTemplate.DEFAULT | model
    result = chain.invoke({"system_prompt": system_prompt, "prompt": prompt})
    return result.content
