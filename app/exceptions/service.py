from starlette import status

from app.config import settings
from app.exceptions.base import ApplicationError


class TokenValidationError(ApplicationError):
    """유효하지 않은 토큰 설정"""

    def __init__(self, x_token):
        self.code = int(f"{settings.SERVICE_CODE}{status.HTTP_401_UNAUTHORIZED}")
        self.message = "Invalid x-token header"
        self.result = {"current_x_token": x_token}


class InvalidReActToolError(ApplicationError):
    """유효하지 않은 ReAct Tool 값 설정"""

    def __init__(self, tool: str):
        self.code = int(f"{settings.SERVICE_CODE}{status.HTTP_400_BAD_REQUEST}")
        self.message = "You have to set available tools to use ReAct Prompting Method: Wikipedia, DuckDuckGoSearch"
        self.result = {"current_tool": tool}


class InvalidLLMProviderNameError(ApplicationError):
    """유효하지 않은 LLM Provider 설정"""

    def __init__(self, llm_provider):
        self.code = int(f"{settings.SERVICE_CODE}{status.HTTP_400_BAD_REQUEST}")
        self.message = "You have to set available LLM provider: Ollama, OpenAI"
        self.result = {"current_llm_provider": llm_provider}


class InvalidDomainError(ApplicationError):
    """유효하지 않은 도메인 설정"""

    def __init__(self, domain: str):
        self.code = int(f"{settings.SERVICE_CODE}{status.HTTP_400_BAD_REQUEST}")
        self.message = "You have to set available Domain: addsub, aqua, coin_flip, commonsensqa, date understanding, " \
                       "gsm8k, last letters, multiarith, shuffled objects, singleeq, strategyqa, svamp"
        self.result = {"current_domain": domain}
