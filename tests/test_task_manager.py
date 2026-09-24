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

    def generate_pdf(text, output_path, mode, source_file, when=None):
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


def test_document_names_are_human():
    from datetime import datetime
    when = datetime(2026, 9, 24, 16, 41)
    assert tm.document_name("Расшифровка", "", when, "txt") == "Расшифровка 24.09.2026 16-41.txt"
    assert (tm.document_name("Конспект лекции", "Лекция: SEO/2026", when, "pdf")
            == "Конспект лекции — Лекция- SEO-2026 — 24.09.2026 16-41.pdf")


def test_prompts_ask_for_content_not_recording():
    from core.prompts import SYSTEM_PROMPT, get_user_prompt
    assert "Никогда не упоминай «транскрибацию»" in SYSTEM_PROMPT
    prompt = get_user_prompt("summary", "раз два три")
    assert "около 3 слов" in prompt and "транскрибац" not in prompt.lower().replace("«транскрибацию»", "")


def test_media_is_deleted_after_transcription_text_stays(manager, tmp_path):
    manager, task, _ = manager
    original = task.work_dir / "original" / "voice.ogg"
    assert original.exists() and not (tmp_path / "voice.ogg").exists()  # перенесён, а не скопирован
    (task.work_dir / "prepared.mp3").write_bytes(b"mp3")
    (task.work_dir / "chunks").mkdir()
    assert asyncio.run(manager.transcribe_task(task))
    assert sorted(p.name for p in task.work_dir.iterdir()) == ["transcript.txt"]


def test_media_is_deleted_even_if_transcription_fails(manager, monkeypatch):
    manager, task, _ = manager

    async def broken(path, language=None):
        raise RuntimeError("boom")

    import core.transcription
    monkeypatch.setattr(core.transcription, "transcribe_audio", broken)
    assert not asyncio.run(manager.transcribe_task(task))
    assert list(task.work_dir.iterdir()) == []


def test_download_folder_is_removed_after_move(tmp_path, monkeypatch):
    import tempfile
    monkeypatch.setattr(settings, "data_dir", str(tmp_path))
    download_dir = tempfile.mkdtemp(dir=str(tmp_path))
    source = f"{download_dir}/big.mp4"
    open(source, "wb").write(b"video")
    task = tm.TaskManager().create_task(source, "", "big.mp4")
    assert not __import__("os").path.exists(download_dir)
    assert (task.work_dir / "original" / "big.mp4").read_bytes() == b"video"


def test_old_folders_on_disk_are_cleaned(tmp_path, monkeypatch):
    import os
    import time as _time
    monkeypatch.setattr(settings, "data_dir", str(tmp_path))
    monkeypatch.setattr(settings, "retention_hours", 168)
    old, fresh = tmp_path / "oldtask", tmp_path / "newtask"
    old.mkdir(); fresh.mkdir()
    (tmp_path / "mtproto_bot.session").write_bytes(b"s")
    week_ago = _time.time() - 8 * 24 * 3600
    os.utime(old, (week_ago, week_ago))
    assert tm.TaskManager().cleanup_old_tasks() == 1
    assert not old.exists() and fresh.exists() and (tmp_path / "mtproto_bot.session").exists()
