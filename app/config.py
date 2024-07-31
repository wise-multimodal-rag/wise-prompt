import logging
from typing import Literal, List, Annotated, Any, Union

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

    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    PORT: int = 8000
    SERVICE_NAME: str = "Python FastAPI Template"
    SERVICE_CODE: int = 100
    MAJOR_VERSION: str = "v1"
    STATUS: str = "dev"

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

    @computed_field  # type: ignore[misc]
    @property
    def log_level(self) -> Any:  # real return type: numeric value (int)
        return logging.getLevelName(self.LEVEL)

    @computed_field  # type: ignore[misc]
    @property
    def server_host(self) -> str:
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"

    # Backend
    BACKEND_CORS_ORIGINS: Annotated[
        Union[List[AnyUrl], str], BeforeValidator(parse_cors)
    ] = []

    # Service Config
    X_TOKEN: str = "wisenut"


settings = Settings()  # type: ignore
