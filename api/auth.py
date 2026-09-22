"""API: авторизация."""
from __future__ import annotations

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import settings

security = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """Проверить Bearer-токен."""
    if not settings.api_auth_token:
        raise HTTPException(status_code=500, detail="API_AUTH_TOKEN не настроен")

    if credentials is None:
        raise HTTPException(status_code=401, detail="Требуется авторизация")

    if credentials.credentials != settings.api_auth_token:
        raise HTTPException(status_code=403, detail="Неверный токен")

    return credentials.credentials
