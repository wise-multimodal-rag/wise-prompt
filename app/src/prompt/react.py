import logging

from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic.v1 import ValidationError

from app.models import LLMProviderRequest
from app.constants import MagicSentence, PromptTemplate
from app.src.exception.service import InvalidTavilySearchTokenError
from app.src.llm_provider.llm_tool import model_setting


def react_prompt(system_prompt, prompt, llm_provider: LLMProviderRequest):
    """
    # TODO: react 직접 구현(적절하지 않은 응답 제공함), langchain 의존성 제거, tavily 의존성 제거

    Args:
        request:

    Returns:

    """
    try:
        tools = [TavilySearchResults(max_results=1)]
    except ValidationError:
        raise InvalidTavilySearchTokenError
    model = model_setting(llm_provider.llm_tool, llm_provider.model, llm_provider.temperature, llm_provider.top_k)
    agent = create_react_agent(model, tools, PromptTemplate.REACT)
    agent_executor = AgentExecutor(
        agent=agent, tools=tools,  # pyright: ignore
        # max_iterations=2,
        early_stopping_method='force',
        # early_stopping_method='generate',
        return_intermediate_steps=True, handle_parsing_errors=True, verbose=True)
    result = agent_executor.invoke(
        {"system_prompt": system_prompt, "input": prompt,
         "magic_sentence": MagicSentence.COT_DEFAULT_MAGIC_SENTENCE})
    logging.debug(f"{result=}")
    answer = result['output']
    return answer
