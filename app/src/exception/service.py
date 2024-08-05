import json
import os

from starlette import status

from app.config import settings


class WisePromptServiceError(Exception):

    def __init__(self, code: int, message: str, result):
        self.code = code
        self.message = message
        self.result = result

    def __str__(self):
        exception_data = {
            "code": self.code,
            "message": self.message,
            "result": self.result
        }
        return json.dumps(exception_data, indent=4, ensure_ascii=False)


class TokenValidationError(WisePromptServiceError):
    """유효하지 않은 토큰 설정"""

    def __init__(self, x_token):
        self.code = int(f"{settings.SERVICE_CODE}{status.HTTP_401_UNAUTHORIZED}")
        self.message = "Invalid x-token header"
        self.result = {"current_x_token": x_token}


class InvalidTavilySearchTokenError(WisePromptServiceError):
    """유효하지 않은 TavilySearch 토큰값 설정"""

    def __init__(self):
        self.code = int(f"{settings.SERVICE_CODE}{status.HTTP_400_BAD_REQUEST}")
        self.message = "You have to set available TAVILY_API_KEY to environment variables to use ReAct Prompting Method."
        self.result = {"TAVILY_API_KEY": os.getenv('TAVILY_API_KEY')}


class InvalidLLMProviderNameError(WisePromptServiceError):
    """유효하지 않은 LLM Provider 설정"""

    def __init__(self, llm_provider):
        self.code = int(f"{settings.SERVICE_CODE}{status.HTTP_400_BAD_REQUEST}")
        self.message = "You have to set available LLM provider: Ollama, OpenAI"
        self.result = {"current_llm_provider": llm_provider}


class InvalidDomainError(WisePromptServiceError):
    """유효하지 않은 도메인 설정"""

    def __init__(self, domain: str):
        self.code = int(f"{settings.SERVICE_CODE}{status.HTTP_400_BAD_REQUEST}")
        self.message = "You have to set available Domain: addsub, aqua, coin_flip, commonsensqa, date understanding, " \
                       "gsm8k, last letters, multiarith, shuffled objects, singleeq, strategyqa, svamp"
        self.result = {"current_domain": domain}
