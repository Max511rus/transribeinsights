"""Порядок работы: сначала расшифровка (отдаётся сразу), потом разбор по выбору."""
import asyncio

import pytest

from config import settings
from core import task_manager as tm


@pytest.fixture
def manager(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", str(tmp_path))
    source = tmp_path / "voice.ogg"
    source.write_bytes(b"audio")
    calls = {"whisper": 0, "llm": []}

    async def prepare_audio_file(path, work_dir):
        return path

    async def transcribe_audio(path, language=None):
        calls["whisper"] += 1
        return "привет это тест"

    async def process_with_llm(text, mode):
        calls["llm"].append(mode)
        return f"# {mode}\n{text}"

    def generate_pdf(text, output_path, mode, source_file):
        open(output_path, "wb").write(b"%PDF")

    import core.audio, core.transcription, core.llm, core.pdf_generator
    monkeypatch.setattr(core.audio, "prepare_audio_file", prepare_audio_file)
    monkeypatch.setattr(core.transcription, "transcribe_audio", transcribe_audio)
    monkeypatch.setattr(core.llm, "process_with_llm", process_with_llm)
    monkeypatch.setattr(core.pdf_generator, "generate_pdf", generate_pdf)
    manager = tm.TaskManager()
    return manager, manager.create_task(str(source), "", "voice.ogg"), calls


def test_transcript_first_then_several_modes_without_new_whisper(manager):
    manager, task, calls = manager
    assert asyncio.run(manager.transcribe_task(task))
    assert (task.work_dir / "transcript.txt").read_text(encoding="utf-8") == task.transcript
    assert task.transcript and calls["llm"] == []  # до выбора режима LLM не вызывается

    assert asyncio.run(manager.analyze_task(task, "insights"))
    assert asyncio.run(manager.analyze_task(task, "summary"))
    assert calls["whisper"] == 1 and calls["llm"] == ["insights", "summary"]
    assert task.status == tm.TaskStatus.COMPLETED and task.pdf_path.endswith("result.pdf")


def test_api_process_task_runs_both_steps(manager):
    manager, task, calls = manager
    task.mode = "lecture"
    asyncio.run(manager.process_task(task))
    assert task.status == tm.TaskStatus.COMPLETED and calls["llm"] == ["lecture"]


def test_invalid_key_is_explained(manager, monkeypatch):
    manager, task, _ = manager

    async def broken(path, language=None):
        raise RuntimeError("Error code: 401 - {'error': {'code': 'invalid_api_key'}}")

    import core.transcription
    monkeypatch.setattr(core.transcription, "transcribe_audio", broken)
    assert not asyncio.run(manager.transcribe_task(task))
    assert "GROQ_API_KEY" in task.error and task.status == tm.TaskStatus.FAILED
