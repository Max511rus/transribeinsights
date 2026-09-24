"""Telegram-бот: обработчики команд и сообщений."""
from __future__ import annotations

import html
import logging
import tempfile
import time
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
from core.prompts import get_mode_title
from core.task_manager import document_name, task_manager
from core.tg_download import BOT_API_LIMIT_MB, download_big, limit_mb

logger = logging.getLogger(__name__)

router = Router()

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

@router.message(F.voice | F.audio | F.video | F.video_note | F.document)
async def handle_file(message: Message):
    """Обработка аудио/видео файлов."""
    if not is_user_allowed(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к этому боту.")
        return

    # Определить тип файла. display_name — имя, которое дал пользователь
    # (у голосовых его нет, тогда в названиях файлов будет только дата)
    file_obj = None
    display_name = ""
    file_name = "audio.ogg"
    file_ext = "ogg"

    if message.voice:
        file_obj = message.voice
        file_name = f"voice_{message.voice.file_unique_id}.ogg"
        file_ext = "ogg"
    elif message.audio:
        file_obj = message.audio
        file_name = message.audio.file_name or f"audio_{message.audio.file_unique_id}.mp3"
        display_name = Path(message.audio.file_name or "").stem or (message.audio.title or "")
        file_ext = Path(file_name).suffix.lstrip(".").lower()
    elif message.video_note:  # «кружочек»
        file_obj = message.video_note
        file_name = f"video_note_{message.video_note.file_unique_id}.mp4"
        file_ext = "mp4"
    elif message.video:
        file_obj = message.video
        file_name = message.video.file_name or f"video_{message.video.file_unique_id}.mp4"
        display_name = Path(message.video.file_name or "").stem
        file_ext = Path(file_name).suffix.lstrip(".").lower()
    elif message.document:
        file_obj = message.document
        file_name = message.document.file_name or "document"
        display_name = Path(message.document.file_name or "").stem
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
    # Bot API отдаёт ботам файлы до 20 МБ; с api_id/api_hash большие качаем через MTProto
    size = file_obj.file_size or 0
    max_mb = limit_mb()
    if size > max_mb * 1024 * 1024:
        text = (f"❌ Файл слишком большой: {size / 1024 / 1024:.1f} МБ\n"
                f"Бот принимает файлы до {max_mb} МБ.")
        if settings.web_transcribe_url:
            text += f"\n\nБольшие файлы можно расшифровать на сайте: {settings.web_transcribe_url}"
        await message.answer(text, parse_mode=None)
        return

    # Скачать файл
    status_msg = await message.answer("⏳ Скачиваю файл...")

    try:
        tmp_dir = tempfile.mkdtemp(dir=str(settings.data_path))
        file_path = str(Path(tmp_dir) / file_name)
        if size > BOT_API_LIMIT_MB * 1024 * 1024:
            await download_big(message.message_id, file_path, _progress_reporter(status_msg, size))
        else:
            bot = message.bot
            file = await bot.get_file(file_obj.file_id)
            await bot.download_file(file.file_path, file_path)
    except Exception as e:
        logger.error(f"Ошибка скачивания файла: {e}")
        await status_msg.edit_text(f"❌ Ошибка при скачивании файла: {html.escape(str(e))}")
        return

    # Шаг 1: расшифровка. Текст отправляется всегда, до выбора режима.
    await status_msg.edit_text("🎧 Расшифровываю…")
    task = task_manager.create_task(file_path, "", file_name)
    task.display_name = display_name
    if not await task_manager.transcribe_task(task):
        await status_msg.edit_text(
            f"❌ <b>Не удалось расшифровать</b>\n\n{html.escape(task.error)}"
        )
        return

    transcript_path = task.work_dir / "transcript.txt"
    await message.answer_document(
        FSInputFile(str(transcript_path), filename=document_name("Расшифровка", display_name, task.local_time, "txt")),
        caption=f"📄 Расшифровка: {len(task.transcript.split())} слов",
    )
    await status_msg.delete()

    # Шаг 2: что сделать с текстом
    _pending_tasks[message.from_user.id] = task.task_id
    await message.answer("Что сделать с текстом?", reply_markup=get_modes_keyboard())


def _progress_reporter(status_msg: Message, total: int):
    """Обновляет «Скачиваю…» не чаще раза в 5 секунд: Telegram ограничивает правки."""
    state = {"last": 0.0}

    async def report(current: int, _total: int) -> None:
        now = time.monotonic()
        if now - state["last"] < 5:
            return
        state["last"] = now
        try:
            await status_msg.edit_text(
                f"⏳ Скачиваю большой файл: {current / 1024 ** 2:.0f} из {total / 1024 ** 2:.0f} МБ "
                f"({current * 100 // max(total, 1)}%)")
        except Exception:  # правка не удалась — не повод прерывать скачивание
            pass

    return report


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
        f"⏳ <b>{MODE_NAMES[mode]}</b>\n\nОбычно это занимает до минуты."
    )

    if not await task_manager.analyze_task(task, mode):
        await callback.message.edit_text(
            f"❌ <b>Ошибка обработки</b> ({MODE_NAMES[mode]})\n\n{html.escape(task.error)}\n\n"
            "Расшифровка сохранена: можно выбрать режим ещё раз.",
            reply_markup=get_modes_keyboard(),
        )
        return

    try:
        if task.pdf_path and Path(task.pdf_path).exists():
            pdf_name = document_name(get_mode_title(mode), task.display_name, task.local_time, "pdf")
            await callback.message.answer_document(
                FSInputFile(task.pdf_path, filename=pdf_name),
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
