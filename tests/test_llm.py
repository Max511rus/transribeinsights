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


def test_output_limit_and_reasoning_are_adjusted(monkeypatch):
    import asyncio
    import types

    import core.llm as llm

    calls = []

    class C:
        class chat:
            class completions:
                @staticmethod
                async def create(**kw):
                    calls.append((kw["max_tokens"], kw.get("extra_body")))
                    if kw["max_tokens"] > 900:
                        raise RuntimeError("Error code: 429 - Request too large for model on output tokens "
                                           "per minute (OTPM): Limit 1000, Requested 1006")
                    if kw.get("extra_body"):
                        raise RuntimeError("Error code: 400 - `reasoning_effort` is not supported")
                    msg = types.SimpleNamespace(content="# Итог")
                    return types.SimpleNamespace(choices=[types.SimpleNamespace(message=msg)], usage=None)

    monkeypatch.setattr(llm, "get_llm_client", lambda: C)
    monkeypatch.setattr(llm, "_limits", {"output_cap": None, "reasoning_param": True})
    monkeypatch.setattr(llm.settings, "llm_max_tokens", 8192)
    assert asyncio.run(llm.call_llm("s", "u")) == "# Итог"
    assert calls == [(8192, {"reasoning_effort": "none"}), (900, {"reasoning_effort": "none"}), (900, None)]


def test_retry_delay_from_message():
    from core.llm import _retry_delay
    assert _retry_delay("Please try again in 7.5s.", 5) == 8.5
    assert _retry_delay("no hint", 5) == 5
