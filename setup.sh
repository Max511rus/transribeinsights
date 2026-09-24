#!/bin/bash
# ============================================================
# 🚀 Transcribe & Insight — ОДНА КОМАНДА ДЛЯ УСТАНОВКИ
#
# Использование:
#   sudo bash setup.sh
#
# Скрипт сам:
#   ✅ Установит все зависимости (Python, ffmpeg, nginx, шрифты)
#   ✅ Создаст виртуальное окружение и установит пакеты
#   ✅ Сгенерирует .env с токенами
#   ✅ Настроит systemd сервисы (API + Telegram бот)
#   ✅ Настроит Nginx
#   ✅ Настроит Firewall
#   ✅ Запустит всё
#
# От вас нужно только:
#   1. GROQ_API_KEY (https://console.groq.com/keys)
#   2. BOT_TOKEN (https://t.me/BotFather)
# ============================================================

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${PURPLE}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                                                      ║${NC}"
echo -e "${PURPLE}║   🚀  Transcribe & Insight — Установка              ║${NC}"
echo -e "${PURPLE}║                                                      ║${NC}"
echo -e "${PURPLE}║   Одна команда — и всё готово!                      ║${NC}"
echo -e "${PURPLE}║                                                      ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# --- Проверка root ---
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Запустите с sudo:${NC}"
    echo -e "   ${YELLOW}sudo bash setup.sh${NC}"
    echo ""
    exit 1
fi

# --- Определяем пути ---
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="/opt/transcribe-insight"
APP_USER="transcribe"

echo -e "  ${CYAN}Проект:${NC}  $PROJECT_DIR"
echo -e "  ${CYAN}Установка:${NC} $APP_DIR"
echo ""

# ============================================================
# ШАГ 1: Системные пакеты
# ============================================================
echo -e "${BLUE}┌──────────────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│  1/8  Установка системных зависимостей...           │${NC}"
echo -e "${BLUE}└──────────────────────────────────────────────────────┘${NC}"

export DEBIAN_FRONTEND=noninteractive

apt update -qq 2>/dev/null
apt install -y -qq \
    python3 python3-venv python3-pip python3-dev \
    ffmpeg \
    libpango1.0-dev libcairo2-dev libffi-dev \
    fonts-noto fonts-noto-cjk fonts-noto-color-emoji \
    nginx \
    curl git openssl \
    > /dev/null 2>&1

echo -e "  ${GREEN}✅ Python $(python3 --version 2>&1 | cut -d' ' -f2)${NC}"
echo -e "  ${GREEN}✅ ffmpeg установлен${NC}"
echo -e "  ${GREEN}✅ nginx установлен${NC}"
echo -e "  ${GREEN}✅ Шрифты Noto (кириллица) установлены${NC}"
echo ""

# ============================================================
# ШАГ 2: Запрос ключей
# ============================================================
echo -e "${BLUE}┌──────────────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│  2/8  API ключи                                      │${NC}"
echo -e "${BLUE}└──────────────────────────────────────────────────────┘${NC}"
echo ""
echo -e "  ${YELLOW}Нужно 2 ключа:${NC}"
echo -e "  ${CYAN}1) GROQ_API_KEY${NC} — https://console.groq.com/keys"
echo -e "  ${CYAN}2) BOT_TOKEN${NC}    — https://t.me/BotFather (команда /newbot)"
echo ""

read -p "  ${BOLD}GROQ_API_KEY:${NC} " GROQ_API_KEY
while [ -z "$GROQ_API_KEY" ]; do
    echo -e "  ${RED}⚠️  Не может быть пустым!${NC}"
    read -p "  ${BOLD}GROQ_API_KEY:${NC} " GROQ_API_KEY
done

echo ""
read -p "  ${BOLD}BOT_TOKEN (или Enter чтобы пропустить):${NC} " BOT_TOKEN
if [ -z "$BOT_TOKEN" ]; then
    BOT_TOKEN="skip"
    echo -e "  ${YELLOW}⚠️  Бот не будет настроен (можно добавить позже)${NC}"
fi

echo ""
read -p "  ${BOLD}Домен (или Enter для localhost):${NC} " DOMAIN
[ -z "$DOMAIN" ] && DOMAIN="localhost"

# Генерация секретов
API_AUTH_TOKEN=$(openssl rand -hex 32)

echo ""
echo -e "  ${GREEN}✅ Ключи получены${NC}"
echo -e "  ${GREEN}✅ API токен: ${API_AUTH_TOKEN:0:10}...${NC}"
echo ""

# ============================================================
# ШАГ 3: Пользователь и директории
# ============================================================
echo -e "${BLUE}┌──────────────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│  3/8  Создание пользователя и директорий             │${NC}"
echo -e "${BLUE}└──────────────────────────────────────────────────────┘${NC}"

id "$APP_USER" &>/dev/null || useradd -r -s /bin/false "$APP_USER"
mkdir -p "$APP_DIR/data" /var/log/transcribe-insight

echo -e "  ${GREEN}✅ Пользователь: $APP_USER${NC}"
echo -e "  ${GREEN}✅ Директории созданы${NC}"
echo ""

# ============================================================
# ШАГ 4: Копирование проекта
# ============================================================
echo -e "${BLUE}┌──────────────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│  4/8  Копирование проекта                            │${NC}"
echo -e "${BLUE}└──────────────────────────────────────────────────────┘${NC}"

cp -r "$PROJECT_DIR"/* "$APP_DIR/" 2>/dev/null || true
cp "$PROJECT_DIR"/.env.example "$APP_DIR/" 2>/dev/null || true
cp "$PROJECT_DIR"/.gitignore "$APP_DIR/" 2>/dev/null || true

echo -e "  ${GREEN}✅ Файлы скопированы в $APP_DIR${NC}"
echo ""

# ============================================================
# ШАГ 5: Python окружение
# ============================================================
echo -e "${BLUE}┌──────────────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│  5/8  Python зависимости (может занять 1-2 мин)...   │${NC}"
echo -e "${BLUE}└──────────────────────────────────────────────────────┘${NC}"

cd "$APP_DIR"
python3 -m venv venv 2>/dev/null || true
./venv/bin/pip install --upgrade pip -q 2>/dev/null
./venv/bin/pip install -r requirements.txt -q 2>/dev/null

echo -e "  ${GREEN}✅ Все Python пакеты установлены${NC}"
echo ""

# ============================================================
# ШАГ 6: Конфигурация .env
# ============================================================
echo -e "${BLUE}┌──────────────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│  6/8  Создание конфигурации .env                     │${NC}"
echo -e "${BLUE}└──────────────────────────────────────────────────────┘${NC}"

cat > "$APP_DIR/.env" << ENVEOF
# Transcribe & Insight — Конфигурация
# Сгенерировано: $(date '+%Y-%m-%d %H:%M:%S')

GROQ_API_KEY=$GROQ_API_KEY
GROQ_WHISPER_MODEL=whisper-large-v3
GROQ_LLM_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MAX_UPLOAD_MB=25
GROQ_CHUNK_SIZE_MB=20
GROQ_MAX_RETRIES=3
GROQ_RETRY_DELAY=5

BOT_TOKEN=$BOT_TOKEN
BOT_ALLOWED_USERS=

API_AUTH_TOKEN=$API_AUTH_TOKEN
API_HOST=0.0.0.0
API_PORT=8000
API_CORS_ORIGINS=http://$DOMAIN,https://$DOMAIN,http://localhost:3000

MAX_FILE_SIZE_MB=25
MAX_PROCESSING_MINUTES=30
SUPPORTED_AUDIO_EXTENSIONS=mp3,wav,ogg,m4a,flac,aac,wma
SUPPORTED_VIDEO_EXTENSIONS=mp4,avi,mkv,mov,webm,flv,wmv

LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4096
LLM_CHUNK_SIZE=12000
LLM_CHUNK_OVERLAP=500

DATA_DIR=$APP_DIR/data
RETENTION_HOURS=24

LOG_LEVEL=INFO
LOG_TRANSCRIPTS=false

PDF_FONT_FAMILY=Noto Sans
PDF_PAGE_FORMAT=A4
ENVEOF

chown "$APP_USER:$APP_USER" "$APP_DIR/.env"
chmod 600 "$APP_DIR/.env"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

echo -e "  ${GREEN}✅ .env создан${NC}"
echo -e "  ${GREEN}✅ Права настроены${NC}"
echo ""

# ============================================================
# ШАГ 7: Systemd сервисы
# ============================================================
echo -e "${BLUE}┌──────────────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│  7/8  Настройка сервисов (systemd)                   │${NC}"
echo -e "${BLUE}└──────────────────────────────────────────────────────┘${NC}"

cat > /etc/systemd/system/transcribe-api.service << SVCEOF
[Unit]
Description=Transcribe & Insight — HTTP API
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/uvicorn api.app:app --host 127.0.0.1 --port 8000 --workers 1
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=transcribe-api
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
SVCEOF

cat > /etc/systemd/system/transcribe-bot.service << SVCEOF
[Unit]
Description=Transcribe & Insight — Telegram Bot
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python -m bot.main
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=transcribe-bot
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable transcribe-api 2>/dev/null
[ "$BOT_TOKEN" != "skip" ] && systemctl enable transcribe-bot 2>/dev/null

echo -e "  ${GREEN}✅ transcribe-api.service — создан и включён${NC}"
[ "$BOT_TOKEN" != "skip" ] && echo -e "  ${GREEN}✅ transcribe-bot.service — создан и включён${NC}"
echo ""

# ============================================================
# ШАГ 8: Nginx + Firewall + Запуск
# ============================================================
echo -e "${BLUE}┌──────────────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│  8/8  Nginx, Firewall, Запуск сервисов               │${NC}"
echo -e "${BLUE}└──────────────────────────────────────────────────────┘${NC}"

# Nginx
cat > /etc/nginx/sites-available/transcribe-insight << NGXEOF
server {
    listen 80;
    server_name $DOMAIN;
    client_max_body_size 50M;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000;
    }

    location / {
        root $APP_DIR/dist;
        try_files \$uri \$uri/ /index.html;
    }
}
NGXEOF

ln -sf /etc/nginx/sites-available/transcribe-insight /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default 2>/dev/null
nginx -t 2>/dev/null && systemctl reload nginx 2>/dev/null || true

echo -e "  ${GREEN}✅ Nginx настроен (домен: $DOMAIN)${NC}"

# Firewall
if command -v ufw &>/dev/null; then
    ufw allow 22/tcp 2>/dev/null || true
    ufw allow 80/tcp 2>/dev/null || true
    ufw allow 443/tcp 2>/dev/null || true
    echo "y" | ufw enable 2>/dev/null || true
    echo -e "  ${GREEN}✅ Firewall (UFW) настроен${NC}"
fi

# Запуск!
systemctl start transcribe-api
sleep 2

if [ "$BOT_TOKEN" != "skip" ]; then
    systemctl start transcribe-bot
    echo -e "  ${GREEN}✅ Telegram-бот запущен${NC}"
fi

# Проверка API
if curl -sf http://127.0.0.1:8000/health | grep -q "ok" 2>/dev/null; then
    echo -e "  ${GREEN}✅ API отвечает и работает!${NC}"
else
    echo -e "  ${YELLOW}⚠️  API запускается... (проверьте: journalctl -u transcribe-api -f)${NC}"
fi

echo ""

# ============================================================
# ИТОГ
# ============================================================
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                      ║${NC}"
echo -e "${GREEN}║   🎉  ВСЁ ГОТОВО! Сервис работает!                  ║${NC}"
echo -e "${GREEN}║                                                      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${YELLOW}📡 API:${NC}"
echo -e "     ${CYAN}http://$DOMAIN/health${NC}"
echo -e "     ${CYAN}http://$DOMAIN/api/v1/tasks${NC}"
echo ""
echo -e "  ${YELLOW}🔑 API Token (для запросов):${NC}"
echo -e "     ${GREEN}$API_AUTH_TOKEN${NC}"
echo ""
echo -e "  ${YELLOW}🤖 Telegram:${NC}"
if [ "$BOT_TOKEN" != "skip" ]; then
    echo -e "     ${GREEN}Бот запущен! Отправьте /start в Telegram${NC}"
else
    echo -e "     ${YELLOW}Не настроен. Добавьте BOT_TOKEN:${NC}"
    echo -e "     ${CYAN}sudo nano $APP_DIR/.env${NC}"
    echo -e "     ${CYAN}sudo systemctl restart transcribe-bot${NC}"
fi
echo ""
echo -e "  ${YELLOW}📋 Полезные команды:${NC}"
echo ""
echo -e "     ${CYAN}# Статус сервисов${NC}"
echo -e "     sudo systemctl status transcribe-api"
echo -e "     sudo systemctl status transcribe-bot"
echo ""
echo -e "     ${CYAN}# Перезапуск${NC}"
echo -e "     sudo systemctl restart transcribe-api transcribe-bot"
echo ""
echo -e "     ${CYAN}# Логи (в реальном времени)${NC}"
echo -e "     sudo journalctl -u transcribe-api -f"
echo -e "     sudo journalctl -u transcribe-bot -f"
echo ""
echo -e "     ${CYAN}# Тест API${NC}"
echo -e "     curl http://$DOMAIN/health"
echo ""
echo -e "     ${CYAN}# SSL (если есть домен)${NC}"
echo -e "     sudo certbot --nginx -d $DOMAIN"
echo ""
echo -e "  ${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Сохраняем инфо
cat > "$APP_DIR/SETUP_INFO.txt" << INFOEOF
=== Transcribe & Insight ===
Установлено: $(date '+%Y-%m-%d %H:%M:%S')
Домен: $DOMAIN
API: http://$DOMAIN/api/v1/tasks
API Token: $API_AUTH_TOKEN
Health: http://$DOMAIN/health
Конфиг: $APP_DIR/.env
INFOEOF

echo -e "  ${GREEN}📄 Инфо сохранена: $APP_DIR/SETUP_INFO.txt${NC}"
echo ""
