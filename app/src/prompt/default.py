from app.schemas.prompt import LLMProviderRequest
from app.constants import PromptTemplate
from app.src.llm_provider.llm_tool import model_setting


def default_prompt(system_prompt, prompt, llm_provider: LLMProviderRequest):
    """Default prompt without any prompt engineering.

    Args:
        system_prompt:
        prompt:
        llm_provider:

    Returns:

    """
    model = model_setting(llm_provider.llm_tool, llm_provider.model, llm_provider.temperature)
    chain = PromptTemplate.DEFAULT | model
    result = chain.invoke({"system_prompt": system_prompt, "prompt": prompt})
    return result.content
