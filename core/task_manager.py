"""Менеджер задач: управление жизненным циклом обработки."""
from __future__ import annotations

import asyncio
import logging
import shutil
import uuid
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)


def describe_error(error: Exception) -> str:
    """Понятный текст ошибки для пользователя."""
    text = str(error)
    if "401" in text or "invalid_api_key" in text or "Invalid API Key" in text:
        return "Groq отклонил ключ (401): проверьте GROQ_API_KEY в .env и перезапустите бота"
    if "403" in text:
        return ("Groq закрыл доступ (403): с этого сервера нужен VPN, "
                "укажите GROQ_PROXY в .env (например socks5://127.0.0.1:1080)")
    return text


class TaskStatus(str, Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    TRANSCRIBING = "transcribing"
    PROCESSING = "processing"
    GENERATING_PDF = "generating_pdf"
    COMPLETED = "completed"
    FAILED = "failed"


class Task:
    """Задача на обработку."""

    def __init__(self, task_id: str, file_path: str, mode: str, file_name: str):
        self.task_id = task_id
        self.file_path = file_path
        self.file_name = file_name
        self.mode = mode
        self.status = TaskStatus.PENDING
        self.progress = 0
        self.transcript = ""
        self.result = ""
        self.pdf_path = ""
        self.error = ""
        self.created_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None

    @property
    def work_dir(self) -> Path:
        return settings.data_path / self.task_id

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "progress": self.progress,
            "file_name": self.file_name,
            "mode": self.mode,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class TaskManager:
    """Управление задачами обработки."""

    def __init__(self):
        self.tasks: dict[str, Task] = {}

    def create_task(self, file_path: str, mode: str, file_name: str) -> Task:
        """Создать новую задачу."""
        task_id = uuid.uuid4().hex[:12]
        task = Task(task_id, file_path, mode, file_name)
        task.work_dir.mkdir(parents=True, exist_ok=True)

        # Скопировать файл в рабочую директорию
        dest = task.work_dir / "original" / file_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, str(dest))

        self.tasks[task_id] = task
        logger.info(f"Задача создана: {task_id} ({file_name}, mode={mode})")
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    async def transcribe_task(self, task: Task) -> bool:
        """Шаг 1: аудио → текст (Whisper). Сохраняет transcript.txt.

        Возвращает True, если расшифровка готова; иначе task.status = FAILED."""
        try:
            from core.audio import prepare_audio_file
            from core.transcription import transcribe_audio
            from core.text_cleaner import clean_transcript

            task.status = TaskStatus.PREPARING
            task.progress = 10
            logger.info(f"[{task.task_id}] Подготовка аудио...")
            audio_path = await prepare_audio_file(task.file_path, str(task.work_dir))

            task.status = TaskStatus.TRANSCRIBING
            task.progress = 25
            logger.info(f"[{task.task_id}] Транскрибация...")
            raw_transcript = await transcribe_audio(audio_path)

            task.progress = 55
            task.transcript = clean_transcript(raw_transcript)
            (task.work_dir / "transcript.txt").write_text(task.transcript, encoding="utf-8")
            logger.info(f"[{task.task_id}] Расшифровка готова ({len(task.transcript)} символов)")
            return True
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = describe_error(e)
            logger.error(f"[{task.task_id}] Ошибка расшифровки: {e}")
            return False

    async def analyze_task(self, task: Task, mode: str) -> bool:
        """Шаг 2: готовый текст → разбор в выбранном режиме (LLM) → PDF.

        Можно вызывать повторно с другим режимом: расшифровка не повторяется."""
        try:
            from core.llm import process_with_llm
            from core.pdf_generator import generate_pdf

            task.mode = mode
            task.error = ""
            task.status = TaskStatus.PROCESSING
            task.progress = 65
            logger.info(f"[{task.task_id}] Обработка LLM (mode={mode})...")
            task.result = await process_with_llm(task.transcript, mode)
            (task.work_dir / "result.md").write_text(task.result, encoding="utf-8")

            task.status = TaskStatus.GENERATING_PDF
            task.progress = 90
            logger.info(f"[{task.task_id}] Генерация PDF...")
            pdf_path = str(task.work_dir / "result.pdf")
            generate_pdf(text=task.result, output_path=pdf_path, mode=mode, source_file=task.file_name)
            task.pdf_path = pdf_path

            task.status = TaskStatus.COMPLETED
            task.progress = 100
            task.completed_at = datetime.utcnow()
            logger.info(f"[{task.task_id}] Задача завершена успешно")
            return True
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = describe_error(e)
            logger.error(f"[{task.task_id}] Ошибка обработки: {e}")
            return False

    async def process_task(self, task: Task) -> None:
        """Полный цикл для HTTP API: расшифровка, затем разбор в task.mode."""
        if await self.transcribe_task(task):
            await self.analyze_task(task, task.mode)

    def cleanup_old_tasks(self) -> int:
        """Удалить старые задачи старше retention_hours."""
        cutoff = datetime.utcnow() - timedelta(hours=settings.retention_hours)
        removed = 0

        for task_id, task in list(self.tasks.items()):
            if task.created_at < cutoff:
                try:
                    shutil.rmtree(task.work_dir, ignore_errors=True)
                except Exception:
                    pass
                del self.tasks[task_id]
                removed += 1
                logger.info(f"Удалена старая задача: {task_id}")

        return removed


# Глобальный менеджер задач
task_manager = TaskManager()
