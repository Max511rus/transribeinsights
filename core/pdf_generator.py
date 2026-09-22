"""Генерация PDF из Markdown через WeasyPrint + Jinja2."""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader

from config import settings
from core.prompts import get_mode_title

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def generate_pdf(
    text: str,
    output_path: str,
    mode: str = "insights",
    source_file: str = "",
) -> str:
    """Сгенерировать PDF из Markdown-текста.

    Args:
        text: Markdown-текст результата
        output_path: путь для сохранения PDF
        mode: режим обработки
        source_file: имя исходного файла

    Returns:
        Путь к созданному PDF.
    """
    try:
        from weasyprint import HTML
    except ImportError:
        raise RuntimeError(
            "WeasyPrint не установлен. Установите: pip install weasyprint. "
            "Также нужны системные зависимости: libpango1.0-dev libcairo2-dev"
        )

    # Конвертация Markdown в HTML
    html_content = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "nl2br"],
    )

    # Рендеринг шаблона
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("report.html")

    rendered_html = template.render(
        title=get_mode_title(mode),
        date=datetime.now().strftime("%d.%m.%Y %H:%M"),
        mode=mode,
        source_file=source_file,
        content=html_content,
        font_family=settings.pdf_font_family,
    )

    # Генерация PDF
    logger.info(f"Генерация PDF: {output_path}")
    HTML(string=rendered_html).write_pdf(output_path)
    logger.info(f"PDF создан: {output_path}")

    return output_path
