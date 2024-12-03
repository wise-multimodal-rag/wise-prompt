"""TODO list.

TODO: ollama 환경변수 설정 or MODELFILE
https://github.com/ollama/ollama/blob/main/docs/modelfile.md#valid-parameters-and-values
TODO: ChatOllama vs Ollama
(시간상 ChatOllama가 더 짧지만 Ollama는 system을 원하는대로 설정할 수 있음. 하지만 system을 구동시에만 바꾸면 되지 않나?)
"""

from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI

from app.config import settings
from app.constants import ModelOption
from app.exceptions.service import InvalidLLMProviderNameError


def openai_model(model_name, temp: float = ModelOption.TEMPERATURE):
    """Setting OpenAI model.

    Args:
        model_name:
        temp:

    Returns:

    """
    client = ChatOpenAI(model=model_name, temperature=temp)
    return client


def ollama_model(model_name: str, temp: float = ModelOption.TEMPERATURE, k: float = ModelOption.TOP_K):
    """Setting ollama model.

    Args:
        model_name:
        temp:
        k:

    Returns:

    """
    client = ChatOllama(base_url=settings.OLLAMA_BASE_URL,
                        model=model_name, temperature=temp, top_k=k)  # pyright: ignore
    return client


def model_setting(llm_tool: str, model_name: str, temp: float = ModelOption.TEMPERATURE):
    """Model settings (ollama, openai).

    Args:
        llm_tool:
        model_name:
        temp:

    Returns:

    """
    model = ollama_model(model_name)  # default
    if llm_tool.lower() == 'ollama':
        model = ollama_model(model_name, temp)
    elif llm_tool.lower() == 'openai':
        model = openai_model(model_name, temp)
    else:
        InvalidLLMProviderNameError(model_name)
    return model
