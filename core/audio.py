"""Обработка аудио: извлечение звука из видео, подготовка файлов."""
from __future__ import annotations

import asyncio
import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


async def check_ffmpeg() -> bool:
    """Проверить доступность ffmpeg."""
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", "-version",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()
    return proc.returncode == 0


async def has_audio_stream(file_path: str) -> bool:
    """Проверить, содержит ли файл аудиопоток."""
    proc = await asyncio.create_subprocess_exec(
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=codec_type",
        "-of", "csv=p=0",
        file_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    return bool(stdout.strip())


async def extract_audio(input_path: str, output_path: str) -> bool:
    """Извлечь аудиопоток из видео/аудио файла в mp3."""
    if not await has_audio_stream(input_path):
        logger.error(f"Файл не содержит аудиопотока: {input_path}")
        return False

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vn",                    # без видео
        "-acodec", "libmp3lame",  # mp3
        "-ac", "1",               # моно
        "-ar", "16000",           # 16kHz
        "-b:a", "64k",            # 64kbps
        output_path,
    ]

    logger.info(f"Извлечение аудио: {input_path} -> {output_path}")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()

    if proc.returncode != 0:
        logger.error(f"ffmpeg ошибка: {stderr.decode()}")
        return False

    logger.info(f"Аудио извлечено: {output_path}")
    return True


async def prepare_audio_file(file_path: str, work_dir: str) -> str:
    """Подготовить аудиофайл для отправки в Groq Whisper.

    Конвертирует в mp3 16kHz mono 64kbps.
    Возвращает путь к подготовленному файлу.
    """
    output_path = str(Path(work_dir) / "prepared.mp3")

    success = await extract_audio(file_path, output_path)
    if not success:
        raise RuntimeError("Не удалось извлечь аудио из файла. Проверьте, что файл содержит звук.")

    return output_path


async def split_audio_chunk(input_path: str, output_path: str,
                            start_sec: int, duration_sec: int) -> bool:
    """Вырезать чанк из аудиофайла."""
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ss", str(start_sec),
        "-t", str(duration_sec),
        "-acodec", "libmp3lame",
        "-ac", "1",
        "-ar", "16000",
        "-b:a", "64k",
        output_path,
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    return proc.returncode == 0


async def get_audio_duration(file_path: str) -> float:
    """Получить длительность аудио в секундах."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        file_path,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    try:
        return float(stdout.strip())
    except (ValueError, TypeError):
        return 0.0


def get_file_size_mb(file_path: str) -> float:
    """Размер файла в мегабайтах."""
    return Path(file_path).stat().st_size / (1024 * 1024)
