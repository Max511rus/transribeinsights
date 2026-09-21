#!/bin/bash
# ============================================================
# Transcribe & Insight — ПОЛНАЯ АВТОМАТИЧЕСКАЯ УСТАНОВКА
# Запуск: sudo bash setup.sh
# Скрипт сам установит всё и настроит сервер
# ============================================================

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${PURPLE}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                                                  ║${NC}"
    echo -e "${PURPLE}║   🚀 Transcribe & Insight — Установка           ║${NC}"
    echo -e "${PURPLE}║                                                  ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "\n${BLUE}━━━ $1 ━━━${NC}"
}

print_ok() {
    echo -e "${GREEN}  ✅ $1${NC}"
}

print_warn() {
    echo -e "${YELLOW}  ⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}  ❌ $1${NC}"
}

# ============================================================
# Проверки
# ============================================================

print_header

if [ "$EUID" -ne 0 ]; then
    print_error "Запустите с sudo: sudo bash setup.sh"
    exit 1
fi

# Определяем директорию проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
APP_DIR="/opt/transcribe-insight"
APP_USER="transcribe"
LOG_DIR="/var/log/transcribe-insight"

echo -e "  Директория проекта: ${YELLOW}$PROJECT_DIR${NC}"
echo -e "  Установка в:        ${YELLOW}$APP_DIR${NC}"
echo ""

# ============================================================
# Запрос ключей
# ============================================================

print_step "1/9 — API ключи (нужно ввести вручную)"
echo ""
echo -e "  ${YELLOW}Получите ключи:${NC}"
echo -e "  • Groq API:  ${BLUE}https://console.groq.com/keys${NC}"
echo -e "  • Bot Token: ${BLUE}https://t.me/BotFather${NC}"
echo ""

read -p "  Введите GROQ_API_KEY: " GROQ_API_KEY
if [ -z "$GROQ_API_KEY" ]; then
    print_error "GROQ_API_KEY не может быть пустым"
    exit 1
fi

read -p "  Введите BOT_TOKEN (Telegram): " BOT_TOKEN
if [ -z "$BOT_TOKEN" ]; then
    print_warn "BOT_TOKEN не указан — бот не будет запущен"
    BOT_TOKEN="not_set"
fi

# Домен (опционально)
echo ""
read -p "  Домен для API (или Enter для localhost): " DOMAIN
if [ -z "$DOMAIN" ]; then
    DOMAIN="localhost"
fi

# Генерация токена для API
API_AUTH_TOKEN=$(openssl rand -hex 32)

print_ok "Ключи получены"
print_ok "API токен сгенерирован: ${API_AUTH_TOKEN:0:8}..."

# ============================================================
# Системные пакеты
# ============================================================

print_step "2/9 — Системные зависимости"

export DEBIAN_FRONTEND=noninteractive

apt update -qq
apt install -y -qq \
    python3 python3-venv python3-pip python3-dev \
    ffmpeg \
    libpango1.0-dev libcairo2-dev libffi-dev \
    fonts-noto fonts-noto-cjk fonts-noto-color-emoji \
    nginx \
    curl wget git \
    > /dev/null 2>&1

print_ok "Python $(python3 --version 2>&1)"
print_ok "ffmpeg $(ffmpeg -version 2>&1 | head -1)"
print_ok "nginx установлен"
print_ok "Шрифты Noto установлены"

# ============================================================
# Пользователь и директории
# ============================================================

print_step "3/9 — Пользователь и директории"

if ! id "$APP_USER" &>/dev/null; then
    useradd -r -s /bin/false "$APP_USER"
    print_ok "Пользователь $APP_USER создан"
else
    print_ok "Пользователь $APP_USER уже существует"
fi

mkdir -p "$APP_DIR/data"
mkdir -p "$LOG_DIR"
print_ok "Директории созданы"

# ============================================================
# Копирование проекта
# ============================================================

print_step "4/9 — Копирование проекта"

# Копируем файлы проекта
cp -r "$PROJECT_DIR"/* "$APP_DIR/" 2>/dev/null || true
cp "$PROJECT_DIR/.env.example" "$APP_DIR/" 2>/dev/null || true
cp "$PROJECT_DIR/.gitignore" "$APP_DIR/" 2>/dev/null || true

print_ok "Файлы скопированы в $APP_DIR"

# ============================================================
# Python окружение
# ============================================================

print_step "5/9 — Python зависимости"

cd "$APP_DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_ok "Виртуальное окружение создано"
fi

./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r requirements.txt -q

print_ok "Python пакеты установлены"

# ============================================================
# Конфигурация .env
# ============================================================

print_step "6/9 — Конфигурация"

cat > "$APP_DIR/.env" << EOF
# ============================================
# Transcribe & Insight — Конфигурация
# Сгенерировано автоматически: $(date)
# ============================================

# --- Groq API ---
GROQ_API_KEY=$GROQ_API_KEY
GROQ_WHISPER_MODEL=whisper-large-v3
GROQ_LLM_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MAX_UPLOAD_MB=25
GROQ_CHUNK_SIZE_MB=20
GROQ_MAX_RETRIES=3
GROQ_RETRY_DELAY=5

# --- Telegram Bot ---
BOT_TOKEN=$BOT_TOKEN
BOT_ALLOWED_USERS=

# --- HTTP API ---
API_AUTH_TOKEN=$API_AUTH_TOKEN
API_HOST=0.0.0.0
API_PORT=8000
API_CORS_ORIGINS=http://$DOMAIN,https://$DOMAIN,http://localhost:3000

# --- Обработка файлов ---
MAX_FILE_SIZE_MB=25
MAX_PROCESSING_MINUTES=30
SUPPORTED_AUDIO_EXTENSIONS=mp3,wav,ogg,m4a,flac,aac,wma
SUPPORTED_VIDEO_EXTENSIONS=mp4,avi,mkv,mov,webm,flv,wmv

# --- LLM ---
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4096
LLM_CHUNK_SIZE=12000
LLM_CHUNK_OVERLAP=500

# --- Хранение данных ---
DATA_DIR=$APP_DIR/data
RETENTION_HOURS=24

# --- Логирование ---
LOG_LEVEL=INFO
LOG_TRANSCRIPTS=false

# --- PDF ---
PDF_FONT_FAMILY=Noto Sans
PDF_PAGE_FORMAT=A4
EOF

chown "$APP_USER:$APP_USER" "$APP_DIR/.env"
chmod 600 "$APP_DIR/.env"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

print_ok ".env создан и настроен"

# ============================================================
# Systemd сервисы
# ============================================================

print_step "7/9 — Systemd сервисы"

# API сервис
cat > /etc/systemd/system/transcribe-api.service << EOF
[Unit]
Description=Transcribe & Insight — HTTP API
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/uvicorn api.app:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=transcribe-api
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Bot сервис
cat > /etc/systemd/system/transcribe-bot.service << EOF
[Unit]
Description=Transcribe & Insight — Telegram Bot
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
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
EOF

systemctl daemon-reload
systemctl enable transcribe-api transcribe-bot 2>/dev/null || true

print_ok "transcribe-api.service создан"
print_ok "transcribe-bot.service создан"

# ============================================================
# Nginx
# ============================================================

print_step "8/9 — Nginx"

cat > /etc/nginx/sites-available/transcribe-insight << EOF
server {
    listen 80;
    server_name $DOMAIN;

    client_max_body_size 50M;

    # API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
    }

    # Health
    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
    }

    # Frontend (статика)
    location / {
        root $APP_DIR/dist;
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

ln -sf /etc/nginx/sites-available/transcribe-insight /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true

nginx -t 2>/dev/null && systemctl reload nginx 2>/dev/null || true

print_ok "Nginx настроен для домена: $DOMAIN"

# ============================================================
# Firewall
# ============================================================

print_step "9/9 — Firewall и запуск"

# UFW
if command -v ufw &>/dev/null; then
    ufw allow 22/tcp 2>/dev/null || true
    ufw allow 80/tcp 2>/dev/null || true
    ufw allow 443/tcp 2>/dev/null || true
    echo "y" | ufw enable 2>/dev/null || true
    print_ok "Firewall настроен"
else
    print_warn "UFW не установлен — пропущено"
fi

# Запуск сервисов
systemctl start transcribe-api 2>/dev/null || true
if [ "$BOT_TOKEN" != "not_set" ]; then
    systemctl start transcribe-bot 2>/dev/null || true
    print_ok "Telegram-бот запущен"
else
    print_warn "Бот не запущен (BOT_TOKEN не указан)"
fi

# Ждём запуска API
sleep 2

# Проверка
if curl -s http://127.0.0.1:8000/health | grep -q "ok"; then
    print_ok "API работает!"
else
    print_warn "API может запускаться... проверьте: sudo journalctl -u transcribe-api -f"
fi

# ============================================================
# Итог
# ============================================================

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                  ║${NC}"
echo -e "${GREEN}║   ✅  УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!              ║${NC}"
echo -e "${GREEN}║                                                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${YELLOW}📡 API:${NC}"
echo -e "     URL:   ${GREEN}http://$DOMAIN/api/v1/tasks${NC}"
echo -e "     Token: ${GREEN}$API_AUTH_TOKEN${NC}"
echo -e "     Health:${GREEN} http://$DOMAIN/health${NC}"
echo ""
echo -e "  ${YELLOW}🤖 Telegram-бот:${NC}"
if [ "$BOT_TOKEN" != "not_set" ]; then
    echo -e "     Статус: ${GREEN}запущен${NC}"
    echo -e "     Отправьте /start боту в Telegram"
else
    echo -e "     Статус: ${YELLOW}не настроен${NC}"
    echo -e "     Добавьте BOT_TOKEN в $APP_DIR/.env"
fi
echo ""
echo -e "  ${YELLOW}📋 Команды управления:${NC}"
echo -e "     ${BLUE}sudo systemctl status transcribe-api${NC}   — статус API"
echo -e "     ${BLUE}sudo systemctl status transcribe-bot${NC}   — статус бота"
echo -e "     ${BLUE}sudo systemctl restart transcribe-api${NC}  — перезапуск API"
echo -e "     ${BLUE}sudo journalctl -u transcribe-api -f${NC}   — логи API"
echo -e "     ${BLUE}sudo journalctl -u transcribe-bot -f${NC}   — логи бота"
echo ""
echo -e "  ${YELLOW}🔧 Обновление:${NC}"
echo -e "     ${BLUE}cd $APP_DIR && sudo git pull${NC}"
echo -e "     ${BLUE}sudo ./venv/bin/pip install -r requirements.txt${NC}"
echo -e "     ${BLUE}sudo systemctl restart transcribe-api transcribe-bot${NC}"
echo ""
echo -e "  ${YELLOW}🔒 SSL (если есть домен):${NC}"
echo -e "     ${BLUE}sudo certbot --nginx -d $DOMAIN${NC}"
echo ""
echo -e "  ${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Сохранить информацию в файл
cat > "$APP_DIR/SETUP_INFO.txt" << EOF
=== Transcribe & Insight — Информация об установке ===
Дата: $(date)
Домен: $DOMAIN

API URL: http://$DOMAIN/api/v1/tasks
API Token: $API_AUTH_TOKEN
Health: http://$DOMAIN/health

Конфиг: $APP_DIR/.env
Данные: $APP_DIR/data
Логи: journalctl -u transcribe-api / transcribe-bot

Команды:
  sudo systemctl status transcribe-api
  sudo systemctl status transcribe-bot
  sudo systemctl restart transcribe-api transcribe-bot
  sudo journalctl -u transcribe-api -f
  sudo journalctl -u transcribe-bot -f
EOF

print_ok "Информация сохранена в $APP_DIR/SETUP_INFO.txt"
echo ""
