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
