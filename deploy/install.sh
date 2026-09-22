#!/bin/bash
# Скрипт автоматической установки Transcribe & Insight
# Запуск: sudo ./deploy/install.sh

set -e

echo "=== Transcribe & Insight — Установка ==="

# Проверка root
if [ "$EUID" -ne 0 ]; then
    echo "Ошибка: запустите с sudo"
    exit 1
fi

APP_DIR="/opt/transcribe-insight"
APP_USER="transcribe"

# 1. Обновление системы
echo "[1/8] Обновление системы..."
apt update && apt upgrade -y

# 2. Установка зависимостей
echo "[2/8] Установка зависимостей..."
apt install -y \
    python3 python3-venv python3-pip python3-dev \
    ffmpeg \
    libpango1.0-dev libcairo2-dev libffi-dev \
    fonts-noto fonts-noto-cjk \
    nginx \
    git

# 3. Создание пользователя
echo "[3/8] Создание пользователя..."
if ! id "$APP_USER" &>/dev/null; then
    useradd -r -s /bin/false "$APP_USER"
    echo "  Пользователь $APP_USER создан"
else
    echo "  Пользователь $APP_USER уже существует"
fi

# 4. Создание директорий
echo "[4/8] Создание директорий..."
mkdir -p "$APP_DIR/data"
mkdir -p /var/log/transcribe-insight

# 5. Копирование файлов (если запускается из репозитория)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "[5/8] Копирование файлов..."
    cp -r "$SCRIPT_DIR"/* "$APP_DIR/"
    cp "$SCRIPT_DIR/.env.example" "$APP_DIR/" 2>/dev/null || true
    cp "$SCRIPT_DIR/.gitignore" "$APP_DIR/" 2>/dev/null || true
else
    echo "[5/8] Файлы уже в $APP_DIR"
fi

# 6. Виртуальное окружение
echo "[6/8] Установка Python-зависимостей..."
cd "$APP_DIR"
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 7. Настройка .env
echo "[7/8] Настройка конфигурации..."
if [ ! -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    API_TOKEN=$(openssl rand -hex 32)
    sed -i "s/API_AUTH_TOKEN=.*/API_AUTH_TOKEN=$API_TOKEN/" "$APP_DIR/.env"
    echo "  .env создан. API_AUTH_TOKEN сгенерирован автоматически."
    echo "  ⚠️  Заполните GROQ_API_KEY и BOT_TOKEN вручную: sudo nano $APP_DIR/.env"
else
    echo "  .env уже существует"
fi

# 8. Systemd
echo "[8/8] Настройка сервисов..."
cp "$APP_DIR/deploy/transcribe-api.service" /etc/systemd/system/
cp "$APP_DIR/deploy/transcribe-bot.service" /etc/systemd/system/

# Права
chown -R "$APP_USER:$APP_USER" "$APP_DIR"
chmod 600 "$APP_DIR/.env"

systemctl daemon-reload
systemctl enable transcribe-api transcribe-bot

echo ""
echo "=== Установка завершена! ==="
echo ""
echo "Следующие шаги:"
echo "1. Заполните .env: sudo nano $APP_DIR/.env"
echo "   - GROQ_API_KEY (https://console.groq.com)"
echo "   - BOT_TOKEN (от @BotFather)"
echo ""
echo "2. Запустите сервисы:"
echo "   sudo systemctl start transcribe-api transcribe-bot"
echo ""
echo "3. Проверьте статус:"
echo "   sudo systemctl status transcribe-api"
echo "   sudo systemctl status transcribe-bot"
echo ""
echo "4. Настройте Nginx (см. deploy/INSTALL.md)"
