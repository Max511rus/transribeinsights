"""Большие файлы через MTProto: настройки, прокси, скачивание."""
import asyncio

import pytest

from config import settings
from core import tg_download


def test_enabled_only_with_both_keys(monkeypatch):
    monkeypatch.setattr(settings, "telegram_api_id", "")
    monkeypatch.setattr(settings, "telegram_api_hash", "abc")
    assert not tg_download.big_files_enabled() and tg_download.limit_mb() == 20
    monkeypatch.setattr(settings, "telegram_api_id", "12345")
    assert tg_download.big_files_enabled() and tg_download.limit_mb() == 2000
    monkeypatch.setattr(settings, "telegram_api_id", "не число")
    assert not tg_download.big_files_enabled()


def test_proxy_url_for_telethon():
    assert tg_download.telethon_proxy("") is None
    assert tg_download.telethon_proxy("socks5h://u:p@127.0.0.1:1080") == {
        "proxy_type": "socks5", "addr": "127.0.0.1", "port": 1080, "username": "u", "password": "p", "rdns": True}
    with pytest.raises(ValueError):
        tg_download.telethon_proxy("ftp://x")


def test_download_big_uses_message_id(monkeypatch, tmp_path):
    class Message:
        media = object()

    class Client:
        async def get_messages(self, entity, ids):
            assert entity is None and ids == 77
            return Message()

        async def download_media(self, message, file, progress_callback):
            open(file, "wb").write(b"video")
            return file

    async def fake_client():
        return Client()

    monkeypatch.setattr(tg_download, "_get_client", fake_client)
    dest = str(tmp_path / "v.mp4")
    assert asyncio.run(tg_download.download_big(77, dest)) == dest
    assert open(dest, "rb").read() == b"video"
