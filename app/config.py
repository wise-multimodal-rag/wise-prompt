import logging
import re
from typing import Literal, List, Annotated, Any, Union, Dict

from pydantic import AnyUrl, BeforeValidator, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> Union[List[str], str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list) or isinstance(v, str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    # Environment: local, staging, production
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    PORT: int = 8000
    SERVICE_NAME: str = "Wise Prompt"
    SERVICE_CODE: int = 121
    MAJOR_VERSION: str = "v1"
    STATUS: str = "dev"

    # Request Server URL
    REQUEST_SERVER_URL: str = ""

    # LOG
    LEVEL: str = "INFO"
    JSON_LOG: bool = False
    LOGURU_FORMAT: str = "<green>{time:YY-MM-DD HH:mm:ss.SSS}</green> | " \
                         "<level>{level: <8}</level> | " \
                         "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> " \
                         "- {process} {thread} {extra[request_id]} <level>{message}</level>"

    # LOG SAVE CONFIG
    SAVE: bool = True
    LOG_SAVE_PATH: str = "./logs"
    ROTATION: str = "00:00"
    RETENTION: str = "10 days"
    COMPRESSION: str = "zip"

    @field_validator('LEVEL')
    def validate_log_level(cls, v):
        if v.upper() not in 'CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET'.split('|'):
            raise ValueError(f"로그레벨 `LEVEL` 은 'CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET' 만 가능. LEVEL={v}")
        return v

    @field_validator('REQUEST_SERVER_URL')
    def valid_server_url(cls, v):
        server_url_regex = r'^https?:\/\/(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+(\/[a-zA-Z0-9-._~:/?#[\]@!$&\'()*+,;=]*)?$'
        pattern = re.compile(server_url_regex)
        if v:
            if bool(pattern.match(v)):
                return v
            else:
                raise ValueError(f"URL Validation Error (regex {pattern=}), current url={v}")
        else:
            return None

    @computed_field  # type: ignore[misc]
    @property
    def log_level(self) -> Any:  # real return type: numeric value (int)
        return logging.getLevelName(self.LEVEL)

    @computed_field  # type: ignore[misc]
    @property
    def servers(self) -> Union[List[Dict[str, str]], None]:
        if self.REQUEST_SERVER_URL:
            return [{"url": f"{self.REQUEST_SERVER_URL}", "description": f"{self.ENVIRONMENT.capitalize()} Server"}]
        else:
            return None

    @computed_field  # type: ignore[misc]
    @property
    def root_path_in_servers(self) -> bool:
        if self.REQUEST_SERVER_URL:
            return False
        else:
            return True

    # Backend
    BACKEND_CORS_ORIGINS: Annotated[Union[List[AnyUrl], str], BeforeValidator(parse_cors)] = []

    # Service Config
    X_TOKEN: str = "wisenut"
    OLLAMA_BASE_URL: str = ""


settings = Settings()  # type: ignore
print(settings.json())
