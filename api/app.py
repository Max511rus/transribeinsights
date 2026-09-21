"""FastAPI HTTP API."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger.info("Transcribe & Insight API запускается...")

    # Создать директорию данных
    settings.data_path.mkdir(parents=True, exist_ok=True)

    # Запустить фоновую очистку старых задач
    import asyncio
    from core.task_manager import task_manager

    async def cleanup_loop():
        while True:
            await asyncio.sleep(3600)  # Каждый час
            try:
                removed = task_manager.cleanup_old_tasks()
                if removed:
                    logger.info(f"Очистка: удалено {removed} старых задач")
            except Exception as e:
                logger.error(f"Ошибка очистки: {e}")

    cleanup_task = asyncio.create_task(cleanup_loop())

    yield

    # Shutdown
    cleanup_task.cancel()
    logger.info("API завершает работу")


def create_app() -> FastAPI:
    """Создать FastAPI приложение."""
    app = FastAPI(
        title="Transcribe & Insight API",
        description="Сервис транскрибации и AI-анализа аудио/видео",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Подключить роуты
    from api.routes import router
    app.include_router(router)

    return app


app = create_app()
