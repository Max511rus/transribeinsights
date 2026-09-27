"""Скачивание звука по ссылке на видео (YouTube, VK, Rutube и др.) через yt-dlp."""
from __future__ import annotations

import asyncio
import logging
import re
from pathlib import Path
from typing import Optional, Tuple

from config import settings

logger = logging.getLogger(__name__)

URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)


def find_url(text: str) -> Optional[str]:
    """Первая http(s)-ссылка в тексте или None."""
    match = URL_RE.search(text or "")
    return match.group(0).rstrip(").,;!?»") if match else None


def _download(url: str, out_dir: str) -> Tuple[str, str]:
    import yt_dlp  # тяжёлый импорт — только когда нужен

    max_bytes = settings.url_max_file_size_mb * 1024 * 1024
    options = {
        # только звук: видео для расшифровки не нужно, так в разы меньше качать
        "format": "bestaudio/best",
        "outtmpl": str(Path(out_dir) / "media.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "max_filesize": max_bytes,
        "retries": 3,
    }
    proxy = settings.url_proxy or settings.groq_proxy
    if proxy:
        options["proxy"] = proxy

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)
        if info.get("_type") == "playlist":
            entries = [e for e in info.get("entries") or [] if e]
            if not entries:
                raise RuntimeError("По ссылке нет видео")
            info = entries[0]
        if info.get("is_live"):
            raise RuntimeError("Прямые трансляции не поддерживаются — пришлите ссылку на запись")
        duration = info.get("duration") or 0
        if duration and duration > settings.url_max_minutes * 60:
            raise RuntimeError(f"Видео длиннее {settings.url_max_minutes} мин. ({duration // 60} мин.)")
        info = ydl.process_ie_result(info, download=True)
        path = ydl.prepare_filename(info)

    files = [p for p in Path(out_dir).iterdir() if p.is_file() and not p.name.endswith(".part")]
    if not Path(path).exists():
        if not files:
            raise RuntimeError(f"Файл больше {settings.url_max_file_size_mb} МБ или не скачался")
        path = str(files[0])
    return path, (info.get("title") or "").strip()


async def download_from_url(url: str, out_dir: str) -> Tuple[str, str]:
    """Скачать звук по ссылке. Возвращает (путь к файлу, название видео)."""
    try:
        return await asyncio.to_thread(_download, url, out_dir)
    except Exception as e:
        text = re.sub(r"\x1b\[[0-9;]*m", "", str(e)).replace("ERROR: ", "")
        text = text.split("; please report this issue")[0]
        logger.error(f"Не удалось скачать {url}: {text}")
        raise RuntimeError(text) from None
