"""Очистка текста транскрибации."""
from __future__ import annotations

import re


def clean_transcript(text: str) -> str:
    """Очистить текст транскрибации.

    - Удаляет лишние пробелы
    - Нормализует абзацы
    - Убирает артефакты распознавания
    - Убирает служебные теги
    - Сохраняет смысл, имена, термины, цифры
    """
    if not text:
        return ""

    # Удалить служебные теги (музыка, аплодисменты и т.п.)
    text = re.sub(
        r'\[(?:музыка|аплодисменты|смех|кашель|тишина|noise|music|applause|laughter|silence)\]',
        '', text, flags=re.IGNORECASE
    )

    # Удалить таймкоды вида [00:00:00] или (00:00)
    text = re.sub(r'\[\d{1,2}:\d{2}(?::\d{2})?\]', '', text)
    text = re.sub(r'\(\d{1,2}:\d{2}(?::\d{2})?\)', '', text)

    # Удалить повторяющиеся символы (заикание распознавания)
    text = re.sub(r'(.)\1{4,}', r'\1\1\1', text)

    # Нормализовать пробелы
    text = re.sub(r'[ \t]+', ' ', text)

    # Удалить пробелы в начале/конце строк
    lines = [line.strip() for line in text.split('\n')]

    # Удалить пустые строки
    lines = [line for line in lines if line]

    # Объединить обратно
    text = '\n\n'.join(lines)

    # Удалить множественные пустые строки
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Удалить пробелы в начале и конце
    text = text.strip()

    return text
