"""Telegram-бот: главный файл."""
from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from config import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Запуск бота."""
    if not settings.bot_token:
        logger.error("BOT_TOKEN не задан в .env")
        sys.exit(1)

    # TELEGRAM_PROXY в .env (например socks5://127.0.0.1:1080), если Telegram
    # с сервера доступен только через VPN
    session = AiohttpSession(proxy=settings.telegram_proxy) if settings.telegram_proxy else None
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )
    dp = Dispatcher()

    # Подключить обработчики
    from bot.handlers import router
    dp.include_router(router)

    logger.info("Telegram-бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
