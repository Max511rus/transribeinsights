"""HTTP-клиент для Groq: напрямую или через прокси (GROQ_PROXY в .env)."""
from __future__ import annotations

from typing import Optional

import httpx

from config import settings


def groq_http_client() -> Optional[httpx.AsyncClient]:
    """None — клиент по умолчанию (учитывает и HTTPS_PROXY из окружения).
    Для socks5:// нужен пакет socksio (есть в requirements.txt)."""
    if not settings.groq_proxy:
        return None
    return httpx.AsyncClient(proxy=settings.groq_proxy, timeout=httpx.Timeout(600, connect=20))
