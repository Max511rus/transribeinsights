"""Разбивка файлов на чанки."""
from __future__ import annotations

import logging
import math
from pathlib import Path

from core.audio import get_audio_duration, split_audio_chunk

logger = logging.getLogger(__name__)


async def split_audio_into_chunks(file_path: str, max_chunk_size_mb: int) -> list[str]:
    """Разбить аудиофайл на чанки по размеру.

    Возвращает список путей к файлам чанков.
    """
    duration = await get_audio_duration(file_path)
    if duration <= 0:
        raise RuntimeError("Не удалось определить длительность аудио")

    file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
    bitrate = file_size_mb / (duration / 60)  # MB per minute

    # Длительность одного чанка в секундах
    chunk_duration_sec = (max_chunk_size_mb / bitrate) * 60 * 0.9  # 90% для запаса

    num_chunks = math.ceil(duration / chunk_duration_sec)
    logger.info(f"Разбивка на {num_chunks} чанков по ~{chunk_duration_sec:.0f}с")

    work_dir = Path(file_path).parent / "chunks"
    work_dir.mkdir(exist_ok=True)

    chunk_paths = []
    for i in range(num_chunks):
        start = int(i * chunk_duration_sec)
        output = str(work_dir / f"chunk_{i:03d}.mp3")
        success = await split_audio_chunk(file_path, output, start, int(chunk_duration_sec))
        if not success:
            raise RuntimeError(f"Не удалось создать чанк {i}")
        chunk_paths.append(output)

    return chunk_paths


def split_text_into_chunks(text: str, chunk_size: int, overlap: int = 500) -> list[str]:
    """Разбить текст на чанки по количеству символов.

    Args:
        text: исходный текст
        chunk_size: максимальный размер чанка в символах
        overlap: перекрытие между чанками

    Returns:
        Список текстовых чанков.
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size

        # Попытаться разбить по границе предложения/абзаца
        if end < len(text):
            # Ищем конец абзаца
            paragraph_break = text.rfind("\n\n", start + chunk_size // 2, end)
            if paragraph_break > start:
                end = paragraph_break + 2
            else:
                # Ищем конец предложения
                sentence_break = text.rfind(". ", start + chunk_size // 2, end)
                if sentence_break > start:
                    end = sentence_break + 2

        chunks.append(text[start:end].strip())
        start = end - overlap

    return chunks
