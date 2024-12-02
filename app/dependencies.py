from typing import Annotated

from fastapi import Security
from fastapi.security import APIKeyHeader

from app.utils.authentication import token_validation

header_scheme = APIKeyHeader(name="x-token")


async def get_token_header(x_token: Annotated[str, Security(header_scheme)]):
    await token_validation(x_token)
