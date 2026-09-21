"""Тесты LLM и очистки вывода."""
import pytest

from core.llm import clean_llm_output


def test_clean_removes_markdown_fence():
    text = "```markdown\n# Заголовок\nТекст\n```"
    result = clean_llm_output(text)
    assert "```markdown" not in result
    assert "```" not in result
    assert "# Заголовок" in result


def test_clean_removes_plain_fence():
    text = "```\n# Заголовок\n```"
    result = clean_llm_output(text)
    assert "```" not in result
    assert "# Заголовок" in result


def test_clean_preserves_normal_text():
    text = "# Заголовок\nОбычный текст без код-блоков"
    result = clean_llm_output(text)
    assert result == text


def test_clean_handles_empty():
    assert clean_llm_output("") == ""


def test_clean_strips_whitespace():
    text = "  \n  Текст  \n  "
    result = clean_llm_output(text)
    assert result == "Текст"
