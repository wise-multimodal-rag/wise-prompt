from app.models import LLMProviderRequest
from app.constants import MagicSentence, PromptTemplate
from app.src.llm_provider.llm_tool import model_setting


def cot_prompt(system_prompt, prompt, llm_provider: LLMProviderRequest):
    model = model_setting(llm_provider.llm_tool, llm_provider.model, llm_provider.temperature, llm_provider.top_k)
    chain = PromptTemplate.COT | model
    result = chain.invoke(
        {"system_prompt": system_prompt, "prompt": prompt,
         "magic_sentence": MagicSentence.COT_DEFAULT_MAGIC_SENTENCE}
    )
    return result.content
