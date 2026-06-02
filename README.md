# 2026-VK-EDU-Web-11-Brizhanskaya-E
Меня зовут Елизавета, я студентка 2-го курса кафедры ИУ8 (Информационная безопасность)
# Домашнее задание 1 - Статическая верстка

## Как открыть проект

### Способ 1: Просто открыть HTML файлы
1. Скачайте или склонируйте репозиторий
2. Откройте папку `public/`
3. Дважды кликните на `index.html` (откроется в браузере)

### Способ 2: Через локальный сервер
```bash
# Если установлен Python
cd public
python -m http.server 8000
# Откройте браузер и перейдите на http://localhost:8000
```
## Страницы сайта

1. index.html - Главная страница со списком вопросов
2. question.html - Страница конкретного вопроса
3. ask.html - Форма добавления вопроса
4. login.html - Форма входа
5. signup.html - Форма регистрации
6. profile.html - Профиль пользователя

#Домашнее задание 2 - Routing, Django, шаблоны

### Как запустить проект

```bash
# 1. Клонировать репозиторий
git clone <url-репозитория>
cd ask_me

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # для Linux/Mac
source venv/Scripts/activate # для Windows в GitBash
# venv\Scripts\activate  # для Windows

# 3. Установить зависимости
pip install django

# 4. Применить миграции
python manage.py migrate

# 5. Запустить сервер
python manage.py runserver

# ДЗ 3

# Ask Me - веб-приложение для вопросов и ответов

## Описание проекта

Проект представляет собой веб-приложение, аналогичное Stack Overflow, где пользователи могут задавать вопросы, отвечать на них, ставить лайки/дизлайки и отмечать правильные ответы.

Проект выполнен в рамках учебного курса по веб-разработке.

## Технологии

- Python 3.12
- Django 6.0
- PostgreSQL 17
- Bootstrap 5 (локально)
- HTML/CSS

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone <url-вашего-репозитория>
cd ask_me

### 2. Создание и активация виртуального окружения

```
python -m venv venv
source venv/Scripts/activate  # Windows GitBash
# или
venv\Scripts\activate  # Windows cmd
```

### 3. Установка зависимостей

```
pip install -r requirements.txt
```
### 4. Настройка переменных окружения
Создайте файл .env в корне проекта со следующим содержимым:
```
SECRET_KEY=ваш_секретный_ключ
DB_NAME=ask_me
DB_USER=postgres
DB_PASSWORD=ваш_пароль
DB_HOST=localhost
DB_PORT=5432
DEBUG=True
```
### 5. Настройка базы данных PostgreSQL
Убедитесь, что PostgreSQL запущен:
```
pg_ctl -D "C:/PostgreSQL/data" start
```
Создайте базу данных:
```
psql -U postgres -c "CREATE DATABASE ask_me;"
```
### 6. Применение миграций
```
python manage.py migrate
```
### 7. Заполнение базы тестовыми данными (опционально)
```
python manage.py fill_db 100
```
### 8. Создание суперпользователя
```
python manage.py createsuperuser
```
### 9. Запуск сервера
```
python manage.py runserver
```
Приложение будет доступно по адресу: http://127.0.0.1:8000

### Структура проекта
```
ask_me/
├── app/                    # Основное приложение
│   ├── models.py          # Модели БД
│   ├── views.py           # Контроллеры
│   ├── admin.py           # Настройка админки
│   ├── urls.py            # Маршруты приложения
│   └── management/        # Кастомные команды
├── ask_pupkin_project/    # Настройки проекта
├── templates/             # HTML-шаблоны
├── static/                # Статические файлы (CSS, JS, изображения)
├── public/                # Статическая верстка (моки)
├── media/                 # Загруженные пользователями файлы
└── requirements.txt       # Зависимости проекта
```
