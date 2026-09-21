# Transcribe & Insight

Сервис транскрибации аудио/видео и AI-анализа через Groq API (Whisper + LLM).

## Возможности

- 🎙️ **Транскрибация** — Groq Whisper API с автоопределением языка
- 🧠 **AI-анализ** — 4 режима: выводы, конспект, резюме, план действий
- 📄 **PDF-отчёты** — красиво оформленные документы с поддержкой русского
- 🤖 **Telegram-бот** — отправка аудио/видео прямо в бота
- 🔌 **REST API** — HTTP API для интеграции с сайтами
- 📦 **Обработка больших файлов** — автоматическая разбивка на чанки

## Структура проекта

```
transcribe-insight/
├── config/          # Конфигурация
├── core/            # Ядро: аудио, транскрибация, LLM, PDF
├── api/             # FastAPI HTTP API
├── bot/             # Telegram-бот (aiogram 3)
├── templates/       # Jinja2 шаблоны для PDF
├── tests/           # Тесты
├── deploy/          # Скрипты деплоя, systemd, nginx
├── data/            # Рабочие файлы задач
└── .env.example     # Пример конфигурации
```

## Быстрый старт

### 1. Клонировать и установить

```bash
git clone <your-repo-url> transcribe-insight
cd transcribe-insight
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Установить системные зависимости

```bash
sudo apt update
sudo apt install -y ffmpeg python3-dev \
  libpango1.0-dev libcairo2-dev libffi-dev \
  fonts-noto fonts-noto-cjk
```

### 3. Настроить .env

```bash
cp .env.example .env
nano .env
```

Обязательные переменные:
- `GROQ_API_KEY` — ключ Groq API
- `BOT_TOKEN` — токен Telegram-бота от @BotFather
- `API_AUTH_TOKEN` — токен для HTTP API (сгенерируйте: `openssl rand -hex 32`)

### 4. Запуск

```bash
# API сервер
uvicorn api.app:app --host 0.0.0.0 --port 8000

# Telegram-бот (в другом терминале)
python -m bot.main
```

## Деплой на Ubuntu 22.04

Полная инструкция в файле [deploy/INSTALL.md](deploy/INSTALL.md).

Кратко:

```bash
# Сделать скрипт установки исполняемым
chmod +x deploy/install.sh

# Запустить установку
sudo ./deploy/install.sh
```

## API Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Проверка здоровья |
| POST | `/api/v1/tasks` | Создать задачу |
| GET | `/api/v1/tasks/{id}` | Статус задачи |
| GET | `/api/v1/tasks/{id}/transcript` | Транскрибация |
| GET | `/api/v1/tasks/{id}/result` | Результат |
| GET | `/api/v1/tasks/{id}/pdf` | Скачать PDF |

### Пример

```bash
# Создать задачу
curl -X POST https://your-domain.com/api/v1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@meeting.mp3" \
  -F "mode=insights"

# Проверить статус
curl https://your-domain.com/api/v1/tasks/TASK_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Режимы обработки

| Ключ | Название | Описание |
|------|----------|----------|
| `insights` | Ключевые выводы | Главные идеи, факты, рекомендации |
| `lecture` | Конспект лекции | Структурированный конспект с тезисами |
| `summary` | Краткое резюме | Сжатое изложение |
| `action_plan` | План действий | Конкретные шаги и сроки |

## Telegram-бот

Команды:
- `/start` — начать работу
- `/help` — справка
- `/modes` — список режимов
- `/status` — статус текущей задачи

Отправьте боту аудио, голосовое сообщение или видео — он предложит выбрать режим обработки.

## Тесты

```bash
pytest tests/ -v
```

## Лицензия

MIT
