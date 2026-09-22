# Инструкция по установке на Ubuntu 22.04

## 1. Подключение к серверу

```bash
ssh user@your-server-ip
```

## 2. Обновление системы

```bash
sudo apt update && sudo apt upgrade -y
```

## 3. Установка зависимостей

```bash
sudo apt install -y \
  python3.10 python3.10-venv python3-pip python3-dev \
  ffmpeg \
  libpango1.0-dev libcairo2-dev libffi-dev \
  fonts-noto fonts-noto-cjk \
  nginx \
  certbot python3-certbot-nginx
```

Проверка:
```bash
python3 --version   # 3.10+
ffmpeg -version     # должен быть установлен
```

## 4. Настройка firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 5. Создание пользователя и директорий

```bash
sudo useradd -r -s /bin/false transcribe
sudo mkdir -p /opt/transcribe-insight
sudo mkdir -p /opt/transcribe-insight/data
sudo mkdir -p /var/log/transcribe-insight
```

## 6. Размещение кода

### Вариант A: через Git
```bash
cd /opt
sudo git clone <your-repo-url> transcribe-insight
```

### Вариант B: загрузить вручную
```bash
# На локальной машине:
tar czf project.tar.gz transcribe-insight/
scp project.tar.gz user@server:/tmp/

# На сервере:
sudo tar xzf /tmp/project.tar.gz -C /opt/
```

## 7. Виртуальное окружение

```bash
cd /opt/transcribe-insight
sudo python3 -m venv venv
sudo ./venv/bin/pip install --upgrade pip
sudo ./venv/bin/pip install -r requirements.txt
```

## 8. Конфигурация .env

```bash
sudo cp .env.example .env
sudo nano .env
```

Заполните:
- `GROQ_API_KEY` — получить на https://console.groq.com
- `BOT_TOKEN` — получить у @BotFather в Telegram
- `API_AUTH_TOKEN` — сгенерировать: `openssl rand -hex 32`

```bash
sudo chown transcribe:transcribe .env
sudo chmod 600 .env
sudo chown -R transcribe:transcribe /opt/transcribe-insight
```

## 9. Systemd сервисы

```bash
# API
sudo cp deploy/transcribe-api.service /etc/systemd/system/
# Бот
sudo cp deploy/transcribe-bot.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable transcribe-api transcribe-bot
sudo systemctl start transcribe-api transcribe-bot
```

Проверка:
```bash
sudo systemctl status transcribe-api
sudo systemctl status transcribe-bot
```

Логи:
```bash
sudo journalctl -u transcribe-api -f
sudo journalctl -u transcribe-bot -f
```

## 10. Nginx

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/transcribe-insight
sudo ln -s /etc/nginx/sites-available/transcribe-insight /etc/nginx/sites-enabled/
# Отредактировать домен в конфиге!
sudo nano /etc/nginx/sites-available/transcribe-insight

sudo nginx -t
sudo systemctl reload nginx
```

## 11. SSL (Let's Encrypt)

```bash
sudo certbot --nginx -d your-domain.com
```

## 12. Проверка

```bash
# API health
curl https://your-domain.com/health

# Должно вернуть:
# {"status":"ok","version":"1.0.0","groq_configured":true}
```

## Обновление

```bash
cd /opt/transcribe-insight
sudo git pull
sudo ./venv/bin/pip install -r requirements.txt
sudo systemctl restart transcribe-api transcribe-bot
```
