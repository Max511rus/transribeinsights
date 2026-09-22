"""Тесты промптов."""
import pytest

from core.prompts import (
    get_mode_title,
    get_system_prompt,
    get_user_prompt,
    get_map_prompt,
    get_reduce_prompt,
)


def test_system_prompt_not_empty():
    prompt = get_system_prompt()
    assert len(prompt) > 0
    assert "аналитик" in prompt.lower() or "Markdown" in prompt


def test_user_prompt_contains_text():
    text = "Тестовый текст транскрибации"
    prompt = get_user_prompt("insights", text)
    assert text in prompt


def test_user_prompt_invalid_mode():
    with pytest.raises(ValueError):
        get_user_prompt("invalid_mode", "text")


def test_all_modes_have_prompts():
    modes = ["insights", "lecture", "summary", "action_plan"]
    for mode in modes:
        prompt = get_user_prompt(mode, "test text")
        assert len(prompt) > 0
        assert "test text" in prompt


def test_map_prompt():
    prompt = get_map_prompt("insights", "фрагмент текста")
    assert "фрагмент текста" in prompt


def test_reduce_prompt():
    prompt = get_reduce_prompt("insights", "фрагмент1\n\nфрагмент2")
    assert "фрагмент1" in prompt


def test_mode_titles():
    assert get_mode_title("insights") == "Ключевые выводы"
    assert get_mode_title("lecture") == "Конспект лекции"
    assert get_mode_title("summary") == "Краткое резюме"
    assert get_mode_title("action_plan") == "План действий"


def test_prompt_ends_with_instruction():
    """Промпты должны содержать инструкцию не оборачивать в код-блок."""
    for mode in ["insights", "lecture", "summary", "action_plan"]:
        prompt = get_user_prompt(mode, "text")
        assert "код-блок" in prompt or "markdown" in prompt.lower()
