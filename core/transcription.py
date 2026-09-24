"""Транскрибация через Groq Whisper API."""
from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path
from typing import Optional

from openai import AsyncOpenAI

from config import settings
from core.http import groq_http_client

logger = logging.getLogger(__name__)


def get_whisper_client() -> AsyncOpenAI:
    """Получить клиент Groq Whisper."""
    return AsyncOpenAI(
        api_key=settings.groq_api_key,
        base_url=settings.groq_base_url,
        http_client=groq_http_client(),
    )


async def transcribe_file(file_path: str, language: Optional[str] = None) -> str:
    """Транскрибировать один аудиофайл через Groq Whisper."""
    client = get_whisper_client()

    kwargs = {
        "model": settings.groq_whisper_model,
        "file": open(file_path, "rb"),
        "response_format": "text",
    }
    if language and language != "auto":
        kwargs["language"] = language

    start_time = time.time()
    logger.info(f"Отправка в Groq Whisper: {Path(file_path).name} "
                f"({Path(file_path).stat().st_size / 1024 / 1024:.1f} MB)")

    for attempt in range(settings.groq_max_retries):
        try:
            response = await client.audio.transcriptions.create(**kwargs)
            elapsed = time.time() - start_time
            logger.info(f"Whisper ответ получен за {elapsed:.1f}с")

            text = response if isinstance(response, str) else response.text
            if settings.log_transcripts:
                logger.debug(f"Транскрибация: {text[:200]}...")
            return text.strip()

        except Exception as e:
            error_str = str(e)
            logger.warning(f"Whisper ошибка (попытка {attempt + 1}/{settings.groq_max_retries}): {error_str}")

            if any(code in error_str for code in ["429", "500", "502", "503", "504"]):
                if attempt < settings.groq_max_retries - 1:
                    delay = settings.groq_retry_delay * (attempt + 1)
                    logger.info(f"Повтор через {delay}с...")
                    await asyncio.sleep(delay)
                    continue
            raise

    raise RuntimeError("Превышено количество попыток транскрибации")


async def transcribe_audio(file_path: str, language: Optional[str] = None) -> str:
    """Транскрибировать аудиофайл.

    Если файл больше лимита — разбивает на чанки.
    """
    from core.chunker import split_audio_into_chunks

    file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)

    if file_size_mb <= settings.groq_max_upload_mb:
        return await transcribe_file(file_path, language)

    logger.info(f"Файл {file_size_mb:.1f}MB > {settings.groq_max_upload_mb}MB, разбиваем на чанки")
    chunks = await split_audio_into_chunks(file_path, settings.groq_chunk_size_mb)

    texts = []
    for i, chunk_path in enumerate(chunks):
        logger.info(f"Транскрибация чанка {i + 1}/{len(chunks)}")
        text = await transcribe_file(chunk_path, language)
        texts.append(text)

    # Очистка временных файлов чанков
    for chunk_path in chunks:
        try:
            Path(chunk_path).unlink()
        except Exception:
            pass

    return "\n\n".join(texts)
