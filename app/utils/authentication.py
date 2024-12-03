from app.config import settings
from app.exceptions.service import TokenValidationError


async def token_validation(x_token):
    if x_token != settings.X_TOKEN:
        raise TokenValidationError(x_token)
