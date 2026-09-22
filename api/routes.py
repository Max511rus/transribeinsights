"""API: маршруты (routes)."""
from __future__ import annotations

import asyncio
import logging
import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse

from api.auth import verify_token
from config import settings
from core.task_manager import TaskManager, task_manager

logger = logging.getLogger(__name__)

router = APIRouter()


# --- Health ---

@router.get("/health")
async def health():
    """Проверка здоровья сервиса."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "groq_configured": bool(settings.groq_api_key),
    }


# --- Tasks ---

@router.post("/api/v1/tasks")
async def create_task(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: str = Form(...),
    _token: str = Depends(verify_token),
):
    """Создать задачу на обработку."""
    # Валидация режима
    valid_modes = ["insights", "lecture", "summary", "action_plan"]
    if mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Недопустимый режим. Доступные: {valid_modes}")

    # Валидация файла
    if not file.filename:
        raise HTTPException(status_code=400, detail="Файл не указан")

    ext = Path(file.filename).suffix.lower().lstrip(".")
    if ext not in settings.all_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат: .{ext}. Допустимые: {settings.all_extensions}"
        )

    # Сохранить файл
    tmp_dir = tempfile.mkdtemp(dir=str(settings.data_path))
    file_path = str(Path(tmp_dir) / file.filename)

    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)

    if file_size_mb > settings.max_file_size_mb:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(
            status_code=413,
            detail=f"Файл слишком большой: {file_size_mb:.1f}MB. Максимум: {settings.max_file_size_mb}MB"
        )

    with open(file_path, "wb") as f:
        f.write(content)

    logger.info(f"Файл получен: {file.filename} ({file_size_mb:.1f}MB)")

    # Создать задачу
    task = task_manager.create_task(file_path, mode, file.filename)

    # Запустить обработку в фоне
    background_tasks.add_task(task_manager.process_task, task)

    return {
        "task_id": task.task_id,
        "status": task.status.value,
        "file_name": task.file_name,
        "mode": task.mode,
    }


@router.get("/api/v1/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    _token: str = Depends(verify_token),
):
    """Получить статус задачи."""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task.to_dict()


@router.get("/api/v1/tasks/{task_id}/transcript")
async def get_transcript(
    task_id: str,
    _token: str = Depends(verify_token),
):
    """Получить транскрибацию."""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    if task.status.value not in ["completed"]:
        raise HTTPException(status_code=400, detail=f"Задача ещё не завершена. Статус: {task.status.value}")

    transcript_path = task.work_dir / "transcript.txt"
    if not transcript_path.exists():
        raise HTTPException(status_code=404, detail="Транскрибация не найдена")

    return FileResponse(
        str(transcript_path),
        media_type="text/plain",
        filename="transcript.txt",
    )


@router.get("/api/v1/tasks/{task_id}/result")
async def get_result(
    task_id: str,
    _token: str = Depends(verify_token),
):
    """Получить обработанный текст."""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    if task.status.value not in ["completed"]:
        raise HTTPException(status_code=400, detail=f"Задача ещё не завершена. Статус: {task.status.value}")

    return {
        "task_id": task.task_id,
        "mode": task.mode,
        "result": task.result,
    }


@router.get("/api/v1/tasks/{task_id}/result/text")
async def get_result_text(
    task_id: str,
    _token: str = Depends(verify_token),
):
    """Получить результат как plain text."""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    result_path = task.work_dir / "result.md"
    if not result_path.exists():
        raise HTTPException(status_code=404, detail="Результат не найден")

    return FileResponse(
        str(result_path),
        media_type="text/markdown",
        filename="result.md",
    )


@router.get("/api/v1/tasks/{task_id}/pdf")
async def get_pdf(
    task_id: str,
    _token: str = Depends(verify_token),
):
    """Скачать PDF."""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    if task.status.value not in ["completed"]:
        raise HTTPException(status_code=400, detail=f"Задача ещё не завершена. Статус: {task.status.value}")

    if not task.pdf_path or not Path(task.pdf_path).exists():
        raise HTTPException(status_code=404, detail="PDF не найден")

    return FileResponse(
        task.pdf_path,
        media_type="application/pdf",
        filename="result.pdf",
    )
