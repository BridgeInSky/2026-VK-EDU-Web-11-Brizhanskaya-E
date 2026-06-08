# AskMe - Вопросы и ответы

Проект по ВЕБ-разработке 

Учебный проект по веб-разработке на Django. Сайт вопросов и ответов с функционалом лайков, тегов, рейтингов и real-time уведомлений.

## Технологии

- **Backend**: Django 5.1, Django REST Framework
- **Database**: PostgreSQL 16
- **Cache & Broker**: Redis
- **Task Queue**: Celery + Celery Beat
- **Real-time**: Centrifugo (WebSocket)
- **Web Server**: Nginx + Gunicorn
- **Frontend**: Bootstrap 5, JavaScript (AJAX, WebSocket)
- **Deployment**: Docker, Docker Compose

## Функциональность

### Реализовано в ДЗ1-ДЗ5
- Регистрация и авторизация пользователей
- Создание вопросов и ответов
- Лайки/дизлайки вопросов и ответов (AJAX)
- Отметка правильного ответа
- Загрузка аватарок пользователей
- Пагинация вопросов и ответов
- Теги вопросов

### Реализовано в ДЗ6
- **Асинхронные задачи**: Celery + Redis
- **Кэширование**: популярные теги и лучшие пользователи (кэш обновляется каждые 10 минут)
- **Real-time уведомления**: Centrifugo (WebSocket) для новых ответов
- **Email уведомления**: MailHog для разработки
- **Полнотекстовый поиск**: PostgreSQL full-text search с debounce

### Реализовано в ДЗ7
- **Настройка Gunicorn**: WSGI сервер с 2 воркерами
- **Простой WSGI скрипт**: отображение GET/POST параметров
- **Настройка Nginx**: отдача статики, проксирование на Gunicorn
- **Proxy_cache**: кэширование ответов на уровне Nginx
- **Нагрузочное тестирование**: Apache Benchmark (ab)

## Запуск проекта

### Требования
- Python 3.11+
- Docker Desktop
- WSL (для нагрузочного тестирования)

### Локальный запуск (Windows + venv)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/bridgeinsky/ask_me.git
cd ask_me

# 2. Создать и активировать виртуальное окружение
python -m venv venv_new
source venv_new/Scripts/activate  # Windows Git Bash

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Создать .env файл (используя .env.example)
cp .env.example .env
# Отредактировать .env (подставить свои пароли)

# 5. Запустить Docker сервисы (PostgreSQL, Redis, Centrifugo, MailHog)
docker-compose up -d

# 6. Выполнить миграции
python manage.py migrate

# 7. Создать суперпользователя
python manage.py createsuperuser

# 8. Загрузить тестовые данные (опционально)
python manage.py fill_db 100

# 9. Запустить Celery worker (в отдельном терминале)
celery -A ask_pupkin_project worker --loglevel=info --pool=solo

# 10. Запустить Celery beat (в отдельном терминале)
celery -A ask_pupkin_project beat --loglevel=info

# 11. Запустить Django
python manage.py runserver
```
### Запуск с Nginx и Gunicorn (ДЗ7)
```
# 1. Запустить Nginx через Docker
docker run -d --name ask_me_nginx -p 8080:8080 \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro \
  -v $(pwd)/static:/static:ro \
  nginx:alpine

# 2. Запустить Gunicorn (в WSL)
cd /mnt/c/Users/brizh/projects/ask_me
source venv_wsl/bin/activate
gunicorn -b 0.0.0.0:8000 ask_pupkin_project.wsgi:application
```
### Структура проекта
```
ask_me/
├── app/                       # Основное приложение
│   ├── models.py              # Модели (Question, Answer, Tag, Profile)
│   ├── views.py               # Контроллеры
│   ├── tasks.py               # Celery задачи
│   ├── forms.py               # Формы
│   └── urls.py                # Маршруты приложения
├── ask_pupkin_project/        # Конфигурация проекта
│   ├── settings.py            # Настройки Django
│   ├── celery.py              # Конфигурация Celery
│   └── urls.py                # Корневые маршруты
├── static/                    # Статические файлы (CSS, JS, img)
├── templates/                 # HTML шаблоны
├── centrifugo/                # Конфиг Centrifugo
├── nginx.conf                 # Конфиг Nginx (ДЗ7)
├── gunicorn.conf.py           # Конфиг Gunicorn (ДЗ7)
├── test_wsgi.py               # Простой WSGI скрипт (ДЗ7)
├── docker-compose.yml         # Docker Compose для всех сервисов
├── requirements.txt           # Зависимости Python
└── .env.example               # Пример переменных окружения
```
### Результаты нагрузочного тестирования (ДЗ7)

