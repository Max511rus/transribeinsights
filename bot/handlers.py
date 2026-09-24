"""Telegram-бот: обработчики команд и сообщений."""
from __future__ import annotations

import html
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

TELEGRAM_DOWNLOAD_LIMIT_MB = 20

# расшифровки, ждущие выбора режима: user_id -> task_id
_pending_tasks: dict = {}

MODE_NAMES = {
    "insights": "💡 Ключевые выводы",
    "lecture": "📚 Конспект лекции",
    "summary": "📝 Краткое резюме",
    "action_plan": "🎯 План действий",
}


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
        "Максимальный размер: 20 МБ (ограничение Telegram)\n\n"
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
        "2. Сразу получите расшифровку в .txt\n"
        "3. Выберите, что сделать с текстом\n"
        "4. Получите PDF; можно выбрать ещё режим\n\n"
        "<b>Режимы:</b>\n"
        "💡 <b>Ключевые выводы</b> — главные идеи и факты\n"
        "📚 <b>Конспект</b> — структурированный конспект\n"
        "📝 <b>Резюме</b> — краткое изложение\n"
        "🎯 <b>План действий</b> — конкретные шаги\n\n"
        "<b>Ограничения:</b>\n"
        "• Макс. размер файла: 20 МБ (ограничение Telegram)\n"
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
    # Telegram отдаёт ботам файлы не больше 20 МБ
    limit_mb = min(settings.max_file_size_mb, TELEGRAM_DOWNLOAD_LIMIT_MB)
    if file_obj.file_size and file_obj.file_size > limit_mb * 1024 * 1024:
        await message.answer(
            f"❌ Файл слишком большой: {file_obj.file_size / 1024 / 1024:.1f} МБ\n"
            f"Максимум: {limit_mb} МБ"
        )
        return

    # Скачать файл
    status_msg = await message.answer("⏳ Скачиваю файл...")

    try:
        bot = message.bot
        file = await bot.get_file(file_obj.file_id)
        tmp_dir = tempfile.mkdtemp(dir=str(settings.data_path))
        file_path = str(Path(tmp_dir) / file_name)
        await bot.download_file(file.file_path, file_path)
    except Exception as e:
        logger.error(f"Ошибка скачивания файла: {e}")
        await status_msg.edit_text(f"❌ Ошибка при скачивании файла: {html.escape(str(e))}")
        return

    # Шаг 1: расшифровка. Текст отправляется всегда, до выбора режима.
    await status_msg.edit_text(f"🎧 Расшифровываю <b>{html.escape(file_name)}</b>…")
    task = task_manager.create_task(file_path, "", file_name)
    if not await task_manager.transcribe_task(task):
        await status_msg.edit_text(
            f"❌ <b>Не удалось расшифровать</b>\n\n📁 {html.escape(file_name)}\n\n{html.escape(task.error)}"
        )
        return

    transcript_path = task.work_dir / "transcript.txt"
    stem = Path(file_name).stem or "transcript"
    await message.answer_document(
        FSInputFile(str(transcript_path), filename=f"{stem}.txt"),
        caption=f"📄 Расшифровка: {len(task.transcript.split())} слов",
    )
    await status_msg.delete()

    # Шаг 2: что сделать с текстом
    _pending_tasks[message.from_user.id] = task.task_id
    await message.answer("Что сделать с текстом?", reply_markup=get_modes_keyboard())


# --- Callback: выбор режима ---

@router.callback_query(F.data.startswith("mode_"))
async def handle_mode_selection(callback: CallbackQuery):
    """Разбор уже готовой расшифровки в выбранном режиме."""
    if not is_user_allowed(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    mode = callback.data.replace("mode_", "")
    if mode not in MODE_NAMES:
        await callback.answer("❌ Неизвестный режим", show_alert=True)
        return

    task = task_manager.get_task(_pending_tasks.get(callback.from_user.id, ""))
    if task is None or not task.transcript:
        await callback.message.edit_text("❌ Расшифровка не найдена. Отправьте файл заново.")
        await callback.answer()
        return

    await callback.answer()
    await callback.message.edit_text(
        f"⏳ <b>{MODE_NAMES[mode]}</b>\n\n📁 {html.escape(task.file_name)}\n\nОбычно это занимает до минуты."
    )

    if not await task_manager.analyze_task(task, mode):
        await callback.message.edit_text(
            f"❌ <b>Ошибка обработки</b>\n\n📁 {html.escape(task.file_name)}\n"
            f"🎛 {MODE_NAMES[mode]}\n\n{html.escape(task.error)}\n\n"
            "Расшифровка сохранена: можно выбрать режим ещё раз.",
            reply_markup=get_modes_keyboard(),
        )
        return

    try:
        stem = Path(task.file_name).stem or "result"
        if task.pdf_path and Path(task.pdf_path).exists():
            await callback.message.answer_document(
                FSInputFile(task.pdf_path, filename=f"{stem}_{mode}.pdf"),
                caption=MODE_NAMES[mode],
            )
        if task.result and len(task.result) < 3500:
            await callback.message.answer(task.result, parse_mode=None)
        await callback.message.delete()
        await callback.message.answer(
            "✅ Готово. Можно выбрать другой режим для этого же текста или отправить новый файл.",
            reply_markup=get_modes_keyboard(),
        )
    except Exception as e:
        logger.error(f"Ошибка отправки результата: {e}")
        await callback.message.answer(f"❌ Ошибка отправки файлов: {html.escape(str(e))}")
