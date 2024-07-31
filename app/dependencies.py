from typing import Annotated

from fastapi import Security
from fastapi.security import APIKeyHeader

from app.config import settings
from app.src.exception.service import TokenValidationError

header_scheme = APIKeyHeader(name="x-token")


async def get_token_header(x_token: Annotated[str, Security(header_scheme)]):
    if x_token != settings.X_TOKEN:
        raise TokenValidationError(x_token)
