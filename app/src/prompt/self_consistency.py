import logging
from collections import defaultdict
from typing import DefaultDict, Any

from app.schemas.models import LLMProviderRequest
from app.constants import MagicSentence, PromptTemplate
from app.src.llm_provider.llm_tool import model_setting


def get_cot_answer_json_format(system_prompt, prompt, llm_provider: LLMProviderRequest):
    """Get CoT Answer from json format.

    Args:
        system_prompt:
        prompt:
        llm_provider:

    Returns:

    """
    model = model_setting(llm_provider.llm_tool, llm_provider.model, llm_provider.temperature)
    chain = PromptTemplate.SELF_CONSISTENCY | model
    answer = chain.invoke({
        "system_prompt": system_prompt, "prompt": prompt,
        "magic_sentence": MagicSentence.COT_DEFAULT_MAGIC_SENTENCE,
        "answer": "[number]"
    })
    logging.debug(f"{answer=}")
    return answer


def get_answer_from_json_object(system_prompt, llm_provider, answer, final_answers):
    """Get answer from json object.

    Args:
        system_prompt:
        llm_provider:
        answer:
        final_answers:

    Returns:

    """
    model = model_setting(llm_provider.llm_tool, llm_provider.model, llm_provider.temperature)
    chain = PromptTemplate.GET_JSON_VALUE | model
    result = chain.invoke({"system_prompt": system_prompt, "json_object": answer, "key": 'answer'})
    final_answers[result.content] += 1
    return final_answers


def self_consistency_prompt(system_prompt, prompt, llm_provider: LLMProviderRequest, num: int):
    """Self consistency prompt.

    Args:
        system_prompt:
        prompt:
        llm_provider:
        num:

    Returns:

    """
    final_answers: DefaultDict[Any, int] = defaultdict(int)
    for i in range(num):
        answer = get_cot_answer_json_format(system_prompt, prompt, llm_provider)
        final_answers = get_answer_from_json_object(system_prompt, llm_provider, answer, final_answers)
    logging.debug(f"{final_answers=}")
    final_answer = max(final_answers, key=lambda x: final_answers[x])
    return final_answer
