import logging
from typing import List, Dict, Any, Union, Tuple

from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper, DuckDuckGoSearchAPIWrapper
from langchain_core.agents import AgentAction

from app.constants import PromptTemplate, MagicSentence
from app.schemas.prompt import LLMProviderRequest
from app.exceptions.service import InvalidReActToolError
from app.src.llm_provider.llm_tool import model_setting


def setting_search_tool(tool_name, top_k_search_result):
    """Search tool settings.

    Args:
        tool_name:
        top_k_search_result:

    Returns:

    """
    if tool_name.lower() == 'wikipedia':
        tools = [WikipediaQueryRun(
            api_wrapper=WikipediaAPIWrapper(lang="kr", top_k_results=top_k_search_result))]  # pyright: ignore
    elif tool_name.lower() == 'duckduckgosearch':
        tools = [DuckDuckGoSearchRun(
            api_wrapper=DuckDuckGoSearchAPIWrapper(region="kr-kr", max_results=top_k_search_result))]
    else:
        raise InvalidReActToolError(tool_name)
    return tools


def react_prompt(system_prompt, prompt, llm_provider: LLMProviderRequest, tool_name: str, top_k_search_result: int,
                 max_iterations: int):
    """ReAct Prompt.

    # TODO: 직접 구현한 검색기 및 정보 제공기를 툴로 사용
    # TODO: langchain 없이 react 직접 구현 (현재 Ollama를 사용할 경우, 거의 응답하지 못함)
    langchain search tools: https://python.langchain.com/v0.2/docs/integrations/tools/#search-tools

    Args:
        system_prompt:
        prompt:
        llm_provider:
        top_k_search_result:
        tool_name:

    Returns:

    """
    tools = setting_search_tool(tool_name, top_k_search_result)
    model = model_setting(llm_provider.llm_tool, llm_provider.model, llm_provider.temperature)
    agent = create_react_agent(model, tools, PromptTemplate.REACT)
    agent_executor = AgentExecutor(
        agent=agent, tools=tools, return_intermediate_steps=True,  # pyright: ignore
        max_iterations=max_iterations,
        # early_stopping_method='generate',
        handle_parsing_errors=True, verbose=True)
    result = agent_executor.invoke(
        {"system_prompt": system_prompt, "input": prompt, "magic_sentence": MagicSentence.COT_DEFAULT_MAGIC_SENTENCE})
    answer = result['output']
    intermediate_steps: List[AgentAction] = result['intermediate_steps']
    logging.debug(f"intermediate steps({len(intermediate_steps)}): {intermediate_steps}")
    logging.debug(f"{answer=}")
    intermediate_steps_return: List[Dict[str, Union[str, Tuple[str, Any]]]] = [
        {'tool': inter.tool, 'tool_input': inter.tool_input, 'log': inter.log, 'result': result}  # pyright: ignore
        for inter, result in intermediate_steps]
    return answer, intermediate_steps_return
