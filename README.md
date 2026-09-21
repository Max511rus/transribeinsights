# 🚀 Transcribe & Insight

**Сервис транскрибации аудио/видео и AI-анализа через Groq API.**

Одна команда — и всё работает: Telegram-бот, HTTP API, генерация PDF.

## ⚡ Быстрый старт (одна команда)

```bash
# 1. Клонируйте репозиторий
git clone <your-repo-url> transcribe-insight
cd transcribe-insight

# 2. Запустите установку
sudo bash setup.sh
```

Скрипт **автоматически**:
- ✅ Установит Python, ffmpeg, nginx, шрифты
- ✅ Создаст виртуальное окружение и установит пакеты
- ✅ Сгенерирует конфигурацию (.env)
- ✅ Настроит systemd сервисы (API + бот)
- ✅ Настроит Nginx и Firewall
- ✅ Запустит всё

От вас нужно только **2 ключа**:
1. `GROQ_API_KEY` — получить на https://console.groq.com/keys
2. `BOT_TOKEN` — получить у @BotFather в Telegram

---

## 🤖 Telegram-бот

После установки отправьте боту:
- `/start` — начать
- Аудио или видео файл — бот предложит выбрать режим

**4 режима обработки:**
| Режим | Описание |
|-------|----------|
| 💡 `insights` | Ключевые выводы из записи |
| 📚 `lecture` | Структурированный конспект |
| 📝 `summary` | Краткое резюме |
| 🎯 `action_plan` | План действий с задачами |

**Результат:** transcript.txt + красивый PDF

---

## 🔌 HTTP API

Все эндпоинты требуют `Authorization: Bearer <TOKEN>`

```bash
# Загрузить файл
curl -X POST http://your-domain/api/v1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@meeting.mp3" \
  -F "mode=insights"

# Проверить статус
curl http://your-domain/api/v1/tasks/TASK_ID \
  -H "Authorization: Bearer YOUR_TOKEN"

# Скачать PDF
curl http://your-domain/api/v1/tasks/TASK_ID/pdf \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o result.pdf
```

**Эндпоинты:**
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Проверка (без авторизации) |
| POST | `/api/v1/tasks` | Создать задачу |
| GET | `/api/v1/tasks/{id}` | Статус |
| GET | `/api/v1/tasks/{id}/transcript` | Транскрибация |
| GET | `/api/v1/tasks/{id}/result` | Результат |
| GET | `/api/v1/tasks/{id}/pdf` | Скачать PDF |

---

## 📋 Управление после установки

```bash
# Статус
sudo systemctl status transcribe-api
sudo systemctl status transcribe-bot

# Перезапуск
sudo systemctl restart transcribe-api transcribe-bot

# Логи (в реальном времени)
sudo journalctl -u transcribe-api -f
sudo journalctl -u transcribe-bot -f

# Остановить
sudo systemctl stop transcribe-api transcribe-bot
```

---

## 🔄 Обновление

```bash
cd /opt/transcribe-insight
sudo git pull
sudo ./venv/bin/pip install -r requirements.txt
sudo systemctl restart transcribe-api transcribe-bot
```

---

## 🔒 SSL (Let's Encrypt)

Если у вас есть домен:

```bash
sudo certbot --nginx -d your-domain.com
```

---

## 📁 Структура проекта

```
transcribe-insight/
├── setup.sh              # ⚡ Установка одной командой
├── .env.example          # Пример конфигурации
├── requirements.txt      # Python зависимости
│
├── config/               # Настройки
│   └── settings.py
│
├── core/                 # Ядро
│   ├── audio.py          # Обработка аудио (ffmpeg)
│   ├── transcription.py  # Groq Whisper API
│   ├── llm.py            # Groq LLM
│   ├── pdf_generator.py  # Генерация PDF
│   ├── prompts.py        # Промпты для 4 режимов
│   ├── chunker.py        # Разбивка больших файлов
│   ├── text_cleaner.py   # Очистка текста
│   └── task_manager.py   # Управление задачами
│
├── api/                  # FastAPI HTTP API
│   ├── app.py
│   ├── routes.py
│   └── auth.py
│
├── bot/                  # Telegram-бот
│   ├── main.py
│   └── handlers.py
│
├── templates/            # PDF шаблоны
│   └── report.html
│
├── deploy/               # Деплой
│   ├── setup.sh          # Расширенный установщик
│   ├── install.sh        # Альтернативный установщик
│   ├── INSTALL.md        # Ручная установка
│   ├── nginx.conf
│   ├── transcribe-api.service
│   └── transcribe-bot.service
│
├── tests/                # Тесты
│   ├── test_config.py
│   ├── test_cleaner.py
│   ├── test_prompts.py
│   ├── test_llm.py
│   └── test_chunker.py
│
└── src/                  # Frontend (React)
    └── ...
```

---

## 🛠 Технологии

- **Python 3.10+** — основной язык
- **FastAPI** — HTTP API
- **aiogram 3** — Telegram-бот
- **Groq API** — Whisper (транскрибация) + LLM (анализ)
- **ffmpeg** — обработка аудио/видео
- **WeasyPrint** — генерация PDF
- **Jinja2** — шаблоны
- **systemd** — автозапуск
- **nginx** — reverse proxy

---

## 📝 Лицензия

MIT
