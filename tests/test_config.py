"""Тесты конфигурации."""
import pytest

from config.settings import Settings


def test_default_settings():
    """Проверка значений по умолчанию."""
    s = Settings()
    assert s.groq_whisper_model == "whisper-large-v3"
    assert s.max_file_size_mb == 25
    assert s.retention_hours == 168  # тексты хранятся неделю


def test_audio_extensions():
    """Проверка списка аудио расширений."""
    s = Settings()
    exts = s.audio_extensions
    assert "mp3" in exts
    assert "wav" in exts
    assert "ogg" in exts


def test_video_extensions():
    """Проверка списка видео расширений."""
    s = Settings()
    exts = s.video_extensions
    assert "mp4" in exts
    assert "mkv" in exts
    assert "avi" in exts


def test_all_extensions():
    """Все расширения объединены."""
    s = Settings()
    all_exts = s.all_extensions
    assert len(all_exts) == len(s.audio_extensions) + len(s.video_extensions)


def test_allowed_users_empty():
    """Пустой список пользователей = все разрешены."""
    s = Settings(bot_allowed_users="")
    assert s.allowed_user_ids == []


def test_allowed_users_list():
    """Список пользователей парсится."""
    s = Settings(bot_allowed_users="123, 456, 789")
    assert s.allowed_user_ids == [123, 456, 789]
