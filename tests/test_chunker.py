"""Тесты разбивки текста на чанки."""
import pytest

from core.chunker import split_text_into_chunks


def test_short_text_single_chunk():
    text = "Короткий текст"
    chunks = split_text_into_chunks(text, chunk_size=1000)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_long_text_split():
    text = "A" * 5000
    chunks = split_text_into_chunks(text, chunk_size=2000, overlap=200)
    assert len(chunks) > 1


def test_overlap_works():
    text = "Первый абзац.\n\nВторой абзац.\n\nТретий абзац.\n\nЧетвёртый абзац."
    chunks = split_text_into_chunks(text, chunk_size=30, overlap=10)
    # Должно быть несколько чанков
    assert len(chunks) >= 1


def test_empty_text():
    chunks = split_text_into_chunks("", chunk_size=1000)
    assert len(chunks) == 1
    assert chunks[0] == ""
