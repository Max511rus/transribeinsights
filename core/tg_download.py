"""Скачивание больших файлов из Telegram (до 2 ГБ) через MTProto.

Bot API, через который работает бот (aiogram), отдаёт ботам файлы только до
20 МБ. Через MTProto — «родной» протокол приложений Telegram — тот же бот с тем
же токеном может скачать файл до 2 ГБ. Для этого нужны api_id и api_hash
приложения (my.telegram.org → API development tools). Через VPN работает так же,
как бот: берётся TELEGRAM_PROXY."""
from __future__ import annotations

import asyncio
import logging
from typing import Callable, Optional
from urllib.parse import urlparse

from config import settings

logger = logging.getLogger(__name__)

BOT_API_LIMIT_MB = 20
MTPROTO_LIMIT_MB = 2000

_client = None
_lock = asyncio.Lock()


def big_files_enabled() -> bool:
    return settings.telegram_api_id.strip().isdigit() and bool(settings.telegram_api_hash.strip())


def limit_mb() -> int:
    return MTPROTO_LIMIT_MB if big_files_enabled() else BOT_API_LIMIT_MB


def telethon_proxy(url: str) -> Optional[dict]:
    """socks5://user:pass@127.0.0.1:1080 → настройки прокси для Telethon."""
    if not url:
        return None
    parsed = urlparse(url)
    kind = {"socks5": "socks5", "socks5h": "socks5", "socks4": "socks4", "http": "http"}.get(parsed.scheme)
    if kind is None or not parsed.hostname or not parsed.port:
        raise ValueError(f"Не понимаю адрес прокси: {url}")
    return {"proxy_type": kind, "addr": parsed.hostname, "port": parsed.port,
            "username": parsed.username, "password": parsed.password, "rdns": True}


async def _get_client():
    global _client
    async with _lock:
        if _client is None or not _client.is_connected():
            from telethon import TelegramClient  # только если включено

            client = TelegramClient(
                str(settings.data_path / "mtproto_bot"),  # ключ сессии, чтобы не входить каждый раз
                int(settings.telegram_api_id),
                settings.telegram_api_hash.strip(),
                proxy=telethon_proxy(settings.telegram_proxy),
                receive_updates=False,  # сообщения получает aiogram, здесь только скачивание
            )
            await client.start(bot_token=settings.bot_token)
            _client = client
            logger.info("MTProto-клиент подключён")
    return _client


async def download_big(message_id: int, dest: str, on_progress: Optional[Callable[[int, int], None]] = None) -> str:
    """Скачивает файл из сообщения message_id (личный чат с ботом) в dest."""
    client = await _get_client()
    message = await client.get_messages(None, ids=message_id)
    if message is None or not message.media:
        raise RuntimeError("Не нашёл сообщение с файлом")
    result = await client.download_media(message, file=dest, progress_callback=on_progress)
    if not result:
        raise RuntimeError("Telegram не отдал файл")
    return str(result)
