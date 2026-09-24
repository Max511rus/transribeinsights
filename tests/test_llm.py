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


def test_clean_llm_output_drops_reasoning():
    from core.llm import clean_llm_output
    assert clean_llm_output("<think>размышляю…\nещё</think>\n\n## Выводы\n- один") == "## Выводы\n- один"
    assert clean_llm_output("<think>оборвалось на полуслове") == ""
    assert clean_llm_output("```markdown\n# Итог\n```") == "# Итог"



def test_empty_answer_is_reported(monkeypatch):
    import asyncio
    import types

    import core.llm as llm

    class C:
        class chat:
            class completions:
                @staticmethod
                async def create(**kw):
                    msg = types.SimpleNamespace(content="<think>долго думаю")
                    return types.SimpleNamespace(choices=[types.SimpleNamespace(message=msg)], usage=None)
    monkeypatch.setattr(llm, "get_llm_client", lambda: C)
    with pytest.raises(llm.EmptyAnswer, match="LLM_MAX_TOKENS"):
        asyncio.run(llm.call_llm("s", "u"))
