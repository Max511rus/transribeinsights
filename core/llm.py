"""Обработка текста через Groq LLM."""
from __future__ import annotations

import asyncio
import logging
import re
import time
from typing import Optional

from openai import AsyncOpenAI

from config import settings
from core.http import groq_http_client
from core.chunker import split_text_into_chunks
from core.prompts import (
    get_map_prompt,
    get_reduce_prompt,
    get_system_prompt,
    get_user_prompt,
)

logger = logging.getLogger(__name__)


def get_llm_client() -> AsyncOpenAI:
    """Получить клиент Groq LLM."""
    return AsyncOpenAI(
        api_key=settings.groq_api_key,
        base_url=settings.groq_base_url,
        http_client=groq_http_client(),
        max_retries=0,  # повторы и подстройку под лимиты делает call_llm
    )


# Бесплатный тариф Groq ограничивает токены ответа в минуту (у Qwen — 1000).
# Лимит узнаём из первого отказа и дальше просим не больше; рассуждения
# модели отключаем (reasoning_effort=none), чтобы токены шли на сам ответ.
_OUTPUT_LIMIT_RE = re.compile(r"output tokens per minute.*?Limit (\d+)", re.IGNORECASE | re.DOTALL)
_RETRY_IN_RE = re.compile(r"try again in ([\d.]+)(ms|s|m)", re.IGNORECASE)
_limits = {"output_cap": None, "reasoning_param": True}


def _retry_delay(error_str: str, fallback: float) -> float:
    match = _RETRY_IN_RE.search(error_str)
    if not match:
        return fallback
    value, unit = float(match.group(1)), match.group(2).lower()
    return min(120.0, value / 1000 if unit == "ms" else value * 60 if unit == "m" else value) + 1


class EmptyAnswer(RuntimeError):
    """Ответ пустой после удаления рассуждений: повтор не поможет."""


async def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Вызвать Groq LLM с повторными попытками."""
    client = get_llm_client()

    attempt = 0
    adjustments = 0
    while attempt < settings.groq_max_retries:
        max_tokens = min(settings.llm_max_tokens, _limits["output_cap"] or settings.llm_max_tokens)
        extra = {"reasoning_effort": "none"} if _limits["reasoning_param"] else None
        try:
            start_time = time.time()
            logger.info(f"Отправка в LLM ({settings.groq_llm_model}), "
                        f"текст: {len(user_prompt)} символов")

            response = await client.chat.completions.create(
                model=settings.groq_llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=settings.llm_temperature,
                max_tokens=max_tokens,
                extra_body=extra,
            )

            elapsed = time.time() - start_time
            logger.info(f"LLM ответ получен за {elapsed:.1f}с, "
                        f"токенов: {response.usage.total_tokens if response.usage else '?'}")

            result = clean_llm_output(response.choices[0].message.content or "")
            if not result:
                raise EmptyAnswer(
                    "Модель не успела дописать ответ (закончился лимит токенов на рассуждения). "
                    "Увеличьте LLM_MAX_TOKENS в .env"
                )
            return result

        except EmptyAnswer:
            raise

        except Exception as e:
            error_str = str(e)
            logger.warning(f"LLM ошибка (попытка {attempt + 1}/{settings.groq_max_retries}): {error_str}")

            # подстройка под лимиты тарифа: это не попытка, а исправление запроса
            limit = _OUTPUT_LIMIT_RE.search(error_str)
            if limit and adjustments < 3 and int(int(limit.group(1)) * 0.9) < max_tokens:
                _limits["output_cap"] = max(128, int(int(limit.group(1)) * 0.9))
                adjustments += 1
                logger.info(f"Лимит ответа тарифа: {limit.group(1)} токенов/мин, просим {_limits['output_cap']}")
                continue
            if _limits["reasoning_param"] and "reasoning" in error_str.lower() and "400" in error_str and adjustments < 3:
                _limits["reasoning_param"] = False
                adjustments += 1
                continue

            if "404" in error_str:
                raise RuntimeError(
                    f"Модель '{settings.groq_llm_model}' не найдена в Groq. "
                    f"Проверьте GROQ_LLM_MODEL в .env. "
                    f"Доступные модели: https://console.groq.com/docs/models"
                )

            if any(code in error_str for code in ["429", "500", "502", "503", "504"]):
                if attempt < settings.groq_max_retries - 1:
                    delay = _retry_delay(error_str, settings.groq_retry_delay * (attempt + 1))
                    logger.info(f"Повтор через {delay:.0f}с...")
                    await asyncio.sleep(delay)
                    attempt += 1
                    continue
            raise

    raise RuntimeError("Превышено количество попыток LLM")


def clean_llm_output(text: str) -> str:
    """Очистить ответ LLM от размышлений (<think>…</think>) и код-блоков."""
    # Qwen3 и другие «думающие» модели пишут рассуждения перед ответом
    if "</think>" in text:
        text = text.rsplit("</think>", 1)[1]
    elif text.lstrip().startswith("<think>"):
        text = ""  # ответ оборвался посреди рассуждений: увеличьте LLM_MAX_TOKENS
    text = text.strip()

    # Удалить обёртку ```markdown ... ```
    if text.startswith("```markdown"):
        text = text[len("```markdown"):].strip()
    elif text.startswith("```"):
        text = text[3:].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    return text


async def process_with_llm(text: str, mode: str) -> str:
    """Обработать текст через LLM в указанном режиме.

    Если текст длинный — использует map-reduce стратегию.
    """
    system_prompt = get_system_prompt()

    # Если текст короткий — отправляем целиком
    if len(text) <= settings.llm_chunk_size:
        user_prompt = get_user_prompt(mode, text)
        return await call_llm(system_prompt, user_prompt)

    # Map-reduce для длинных текстов
    logger.info(f"Текст длинный ({len(text)} символов), используем map-reduce")
    chunks = split_text_into_chunks(text, settings.llm_chunk_size, settings.llm_chunk_overlap)
    logger.info(f"Разбит на {len(chunks)} фрагментов")

    # Map: обрабатываем каждый фрагмент
    intermediate_results = []
    for i, chunk in enumerate(chunks):
        logger.info(f"Map: обработка фрагмента {i + 1}/{len(chunks)}")
        map_prompt = get_map_prompt(mode, chunk)
        result = await call_llm(system_prompt, map_prompt)
        intermediate_results.append(result)

    # Reduce: объединяем результаты
    logger.info("Reduce: объединение результатов")
    fragments_text = "\n\n---\n\n".join(
        f"### Фрагмент {i + 1}\n{r}" for i, r in enumerate(intermediate_results)
    )
    reduce_prompt = get_reduce_prompt(mode, fragments_text)
    final_result = await call_llm(system_prompt, reduce_prompt)

    return final_result
