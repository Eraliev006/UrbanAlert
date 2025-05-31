# FixKG Backend

![Python](https://img.shields.io/badge/Python-3.13%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Redis](https://img.shields.io/badge/Redis-7.2-red)

Сервис для управления жалобами и комментариями с системой уведомлений.

## Основные возможности

- 📝 Управление жалобами (CRUD)
- 💬 Комментарии к жалобам
- 🔐 JWT-аутентификация
- ✉️ Уведомления через Email и WebSocket
- 🚀 Асинхронное API на FastAPI

## Технологии

- **Backend**: FastAPI + Python 3.13
- **База данных**: PostgreSQL
- **Кэширование**: Redis
- **Контейнеризация**: Docker

## Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone https://github.com/Eraliev006/UrbanAlert
cd fixkg

# 2. Запустить сервисы
docker-compose up -d --build

# 3. Приложение доступно на:
http://localhost:8000
```

## Environment Configuration (.env)

Create `.env` file with following template:

```
### JWT Settings ###
jwt__secret_key=your_random_secret_key_here
jwt__access_expires_in_minutes=15
jwt__refresh_expires_in_minutes=1440
jwt__algorithm=HS256

### Database Settings ###
database__db_port=5432
database__db_user=db_username
database__db_name=database_name
database__db_password=strong_db_password
database__db_host=localhost

### Email Settings ###
smtp__user_email=your_email@example.com
smtp__password=your_email_password
smtp__hostname=smtp.example.com
smtp__port=587

### Redis Settings ###
redis__port=6379
redis__host=127.0.0.1
```