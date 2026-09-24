"""Конфигурация приложения."""
from __future__ import annotations

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения."""

    # Groq
    groq_api_key: str = ""
    groq_whisper_model: str = "whisper-large-v3"
    groq_llm_model: str = "qwen/qwen3.8-27b"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_max_upload_mb: int = 25
    groq_chunk_size_mb: int = 20
    groq_max_retries: int = 3
    groq_retry_delay: int = 5

    # Telegram
    bot_token: str = ""
    bot_allowed_users: str = ""

    # VPN/прокси, если Telegram или Groq с сервера напрямую недоступны,
    # например socks5://127.0.0.1:1080 (Xray). Пусто — напрямую.
    telegram_proxy: str = ""
    groq_proxy: str = ""

    # веб-версия транскрибации: бот подскажет её для файлов больше 20 МБ
    web_transcribe_url: str = ""

    # api_id и api_hash приложения с my.telegram.org: с ними бот скачивает файлы
    # до 2 ГБ через MTProto (без них — только до 20 МБ, ограничение Bot API)
    telegram_api_id: str = ""
    telegram_api_hash: str = ""

    # API
    api_auth_token: str = ""
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: str = "*"

    # Files
    max_file_size_mb: int = 25
    max_processing_minutes: int = 30
    supported_audio_extensions: str = "mp3,wav,ogg,oga,opus,m4a,flac,aac,wma,amr"
    supported_video_extensions: str = "mp4,m4v,avi,mkv,mov,webm,flv,wmv,3gp"

    # LLM
    llm_temperature: float = 0.3
    llm_max_tokens: int = 8192
    llm_chunk_size: int = 12000
    llm_chunk_overlap: int = 500

    # Storage
    data_dir: str = "./data"
    retention_hours: int = 168  # тексты хранятся неделю; аудио/видео удаляются сразу

    # Logging
    log_level: str = "INFO"
    log_transcripts: bool = False

    # PDF
    pdf_font_family: str = "Noto Sans"
    pdf_page_format: str = "A4"

    @property
    def audio_extensions(self) -> List[str]:
        return [e.strip().lower() for e in self.supported_audio_extensions.split(",")]

    @property
    def video_extensions(self) -> List[str]:
        return [e.strip().lower() for e in self.supported_video_extensions.split(",")]

    @property
    def all_extensions(self) -> List[str]:
        return self.audio_extensions + self.video_extensions

    @property
    def allowed_user_ids(self) -> List[int]:
        if not self.bot_allowed_users.strip():
            return []
        return [int(uid.strip()) for uid in self.bot_allowed_users.split(",") if uid.strip()]

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.api_cors_origins.split(",") if o.strip()]

    @property
    def data_path(self) -> Path:
        p = Path(self.data_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
