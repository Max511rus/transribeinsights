"""Telegram-бот: обработчики команд и сообщений."""
from __future__ import annotations

import asyncio
import logging
import tempfile
from pathlib import Path

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import settings
from core.task_manager import task_manager

logger = logging.getLogger(__name__)

router = Router()


# --- Клавиатуры ---

def get_modes_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора режима."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💡 Ключевые выводы", callback_data="mode_insights"),
            InlineKeyboardButton(text="📚 Конспект", callback_data="mode_lecture"),
        ],
        [
            InlineKeyboardButton(text="📝 Резюме", callback_data="mode_summary"),
            InlineKeyboardButton(text="🎯 План действий", callback_data="mode_action_plan"),
        ],
    ])


# --- Проверка доступа ---

def is_user_allowed(user_id: int) -> bool:
    """Проверить, разрешён ли пользователю доступ."""
    allowed = settings.allowed_user_ids
    if not allowed:
        return True  # Если список пуст — все разрешены
    return user_id in allowed


# --- Команды ---

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Команда /start."""
    if not is_user_allowed(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к этому боту.")
        return

    await message.answer(
        "👋 <b>Привет!</b>\n\n"
        "Я — <b>Transcribe & Insight</b>.\n\n"
        "Отправь мне аудио или видео, и я:\n"
        "• Транскрибирую его в текст\n"
        "• Проанализирую с помощью AI\n"
        "• Создам красивый PDF\n\n"
        "Поддерживаемые форматы:\n"
        "🎵 Аудио: MP3, WAV, OGG, M4A, FLAC\n"
        "🎬 Видео: MP4, AVI, MKV, MOV, WebM\n\n"
        "Максимальный размер: 25 МБ\n\n"
        "Команды:\n"
        "/help — справка\n"
        "/modes — режимы обработки",
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Команда /help."""
    await message.answer(
        "📖 <b>Как пользоваться:</b>\n\n"
        "1. Отправьте аудио или видео файл\n"
        "2. Выберите режим обработки\n"
        "3. Дождитесь результата\n"
        "4. Получите transcript.txt и PDF\n\n"
        "<b>Режимы:</b>\n"
        "💡 <b>Ключевые выводы</b> — главные идеи и факты\n"
        "📚 <b>Конспект</b> — структурированный конспект\n"
        "📝 <b>Резюме</b> — краткое изложение\n"
        "🎯 <b>План действий</b> — конкретные шаги\n\n"
        "<b>Ограничения:</b>\n"
        "• Макс. размер файла: 25 МБ\n"
        "• Обработка может занять 1-5 минут",
        parse_mode="HTML",
    )


@router.message(Command("modes"))
async def cmd_modes(message: Message):
    """Команда /modes — показать режимы."""
    await message.answer(
        "🎛 <b>Режимы обработки:</b>\n\n"
        "💡 <b>Ключевые выводы</b> — извлечение главных идей\n"
        "📚 <b>Конспект лекции</b> — структурированный конспект\n"
        "📝 <b>Краткое резюме</b> — сжатое изложение\n"
        "🎯 <b>План действий</b> — задачи и сроки\n\n"
        "Отправьте файл, чтобы выбрать режим.",
        parse_mode="HTML",
    )


# --- Обработка файлов ---

@router.message(F.voice | F.audio | F.video | F.document)
async def handle_file(message: Message):
    """Обработка аудио/видео файлов."""
    if not is_user_allowed(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к этому боту.")
        return

    # Определить тип файла
    file_obj = None
    file_name = "audio.ogg"
    file_ext = "ogg"

    if message.voice:
        file_obj = message.voice
        file_name = f"voice_{message.voice.file_unique_id}.ogg"
        file_ext = "ogg"
    elif message.audio:
        file_obj = message.audio
        file_name = message.audio.file_name or f"audio_{message.audio.file_unique_id}.mp3"
        file_ext = Path(file_name).suffix.lstrip(".").lower()
    elif message.video:
        file_obj = message.video
        file_name = message.video.file_name or f"video_{message.video.file_unique_id}.mp4"
        file_ext = Path(file_name).suffix.lstrip(".").lower()
    elif message.document:
        file_obj = message.document
        file_name = message.document.file_name or "document"
        file_ext = Path(file_name).suffix.lstrip(".").lower()

    # Проверить расширение
    if file_ext not in settings.all_extensions:
        await message.answer(
            f"❌ Неподдерживаемый формат: .{file_ext}\n\n"
            f"Допустимые:\n"
            f"🎵 Аудио: {', '.join(settings.audio_extensions)}\n"
            f"🎬 Видео: {', '.join(settings.video_extensions)}"
        )
        return

    # Проверить размер
    if file_obj.file_size and file_obj.file_size > settings.max_file_size_mb * 1024 * 1024:
        await message.answer(
            f"❌ Файл слишком большой: {file_obj.file_size / 1024 / 1024:.1f} МБ\n"
            f"Максимум: {settings.max_file_size_mb} МБ"
        )
        return

    # Скачать файл
    status_msg = await message.answer("⏳ Скачиваю файл...")

    try:
        bot = message.bot
        file = await bot.get_file(file_obj.file_id)

        # Сохранить во временную папку
        tmp_dir = tempfile.mkdtemp(dir=str(settings.data_path))
        file_path = str(Path(tmp_dir) / file_name)

        await bot.download_file(file.file_path, file_path)

        # Сохранить путь к файлу в данных пользователя
        # Используем chat_id как ключ для хранения pending file
        pending_files = router.data.setdefault("pending_files", {})
        pending_files[message.from_user.id] = {
            "file_path": file_path,
            "file_name": file_name,
        }

        await status_msg.edit_text(
            f"✅ Файл получен: <b>{file_name}</b>\n\n"
            f"Выберите режим обработки:",
            reply_markup=get_modes_keyboard(),
        )

    except Exception as e:
        logger.error(f"Ошибка скачивания файла: {e}")
        await status_msg.edit_text(f"❌ Ошибка при скачивании файла: {e}")


# --- Callback: выбор режима ---

@router.callback_query(F.data.startswith("mode_"))
async def handle_mode_selection(callback: CallbackQuery):
    """Обработка выбора режима."""
    if not is_user_allowed(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    mode = callback.data.replace("mode_", "")
    valid_modes = ["insights", "lecture", "summary", "action_plan"]

    if mode not in valid_modes:
        await callback.answer("❌ Неизвестный режим", show_alert=True)
        return

    # Получить сохранённый файл
    pending_files = router.data.get("pending_files", {})
    file_info = pending_files.pop(callback.from_user.id, None)

    if not file_info:
        await callback.message.edit_text(
            "❌ Файл не найден. Отправьте файл заново."
        )
        await callback.answer()
        return

    await callback.answer()

    # Обновить сообщение
    mode_names = {
        "insights": "💡 Ключевые выводы",
        "lecture": "📚 Конспект лекции",
        "summary": "📝 Краткое резюме",
        "action_plan": "🎯 План действий",
    }

    await callback.message.edit_text(
        f"⏳ <b>Обработка...</b>\n\n"
        f"📁 Файл: {file_info['file_name']}\n"
        f"🎛 Режим: {mode_names[mode]}\n\n"
        f"Это может занять 1-5 минут.",
    )

    # Создать и запустить задачу
    task = task_manager.create_task(
        file_info["file_path"],
        mode,
        file_info["file_name"],
    )

    # Обработать задачу
    await task_manager.process_task(task)

    # Отправить результат
    if task.status.value == "completed":
        try:
            # transcript.txt
            transcript_path = task.work_dir / "transcript.txt"
            if transcript_path.exists():
                await callback.message.answer_document(
                    FSInputFile(str(transcript_path), filename="transcript.txt"),
                    caption="📄 Транскрибация",
                )

            # PDF
            if task.pdf_path and Path(task.pdf_path).exists():
                await callback.message.answer_document(
                    FSInputFile(task.pdf_path, filename="result.pdf"),
                    caption=f"📊 Результат: {mode_names[mode]}",
                )

            # Preview
            if task.result and len(task.result) < 3000:
                await callback.message.answer(
                    f"<b>📋 Превью:</b>\n\n{task.result[:2000]}",
                    parse_mode="HTML",
                )

            await callback.message.answer("✅ Готово! Отправьте ещё файл для обработки.")

        except Exception as e:
            logger.error(f"Ошибка отправки результата: {e}")
            await callback.message.answer(f"❌ Ошибка отправки файлов: {e}")
    else:
        await callback.message.edit_text(
            f"❌ <b>Ошибка обработки</b>\n\n"
            f"📁 Файл: {file_info['file_name']}\n"
            f"🎛 Режим: {mode_names[mode]}\n\n"
            f"Ошибка: {task.error}",
        )
