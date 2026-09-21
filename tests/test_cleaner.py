"""Тесты очистки текста."""
import pytest

from core.text_cleaner import clean_transcript


def test_clean_empty():
    assert clean_transcript("") == ""


def test_clean_removes_music_tags():
    text = "Привет [музыка] мир [аплодисменты]"
    result = clean_transcript(text)
    assert "[музыка]" not in result
    assert "[аплодисменты]" not in result
    assert "Привет" in result
    assert "мир" in result


def test_clean_removes_timestamps():
    text = "[00:01:23] Привет, [00:02] как дела"
    result = clean_transcript(text)
    assert "[00:01:23]" not in result
    assert "[00:02]" not in result
    assert "Привет" in result


def test_clean_normalizes_spaces():
    text = "Привет    мир    как   дела"
    result = clean_transcript(text)
    assert "    " not in result
    assert "Привет мир" in result


def test_clean_removes_extra_newlines():
    text = "Первый\n\n\n\nВторой"
    result = clean_transcript(text)
    assert "\n\n\n" not in result


def test_clean_preserves_numbers():
    text = "Выручка 247 миллионов, рост 18%"
    result = clean_transcript(text)
    assert "247" in result
    assert "18%" in result


def test_clean_removes_repeated_chars():
    text = "Привееееееет"
    result = clean_transcript(text)
    # Должно сократить повторяющиеся символы
    assert "еееее" not in result
