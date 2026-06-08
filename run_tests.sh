#!/bin/bash

# Создаём папку для результатов
mkdir -p ab_results

# Останавливаем предыдущие процессы
pkill -f gunicorn 2>/dev/null
pkill -f nginx 2>/dev/null

echo "========================================="
echo "Нагрузочное тестирование nginx vs gunicorn"
echo "========================================="

# Запуск Gunicorn для Django (порт 8000)
echo "Запуск Gunicorn с Django..."
cd ~/projects/ask_me
source venv_new/Scripts/activate
gunicorn -c gunicorn.conf.py ask_pupkin_project.wsgi:application &
sleep 3

# Запуск простого WSGI приложения (порт 8081)
echo "Запуск простого WSGI приложения..."
gunicorn wsgi_simple:application -b 127.0.0.1:8081 --workers=2 &
sleep 2

# Запуск Nginx (порт 8080)
echo "Запуск Nginx..."
nginx -c $(pwd)/nginx.conf -p $(pwd)/
sleep 2

echo ""
echo "=== ТЕСТ 1: Статика через nginx ==="
ab -n 1000 -c 10 http://localhost:8080/static/sample.html 2>&1 | tee ab_results/static_nginx.txt

echo ""
echo "=== ТЕСТ 2: Статика через gunicorn ==="
# Копируем файл в uploads для теста
cp static/sample.html uploads/sample.html
ab -n 1000 -c 10 http://localhost:8000/static/sample.html 2>&1 | tee ab_results/static_gunicorn.txt

echo ""
echo "=== ТЕСТ 3: Динамика через gunicorn (прямо) ==="
ab -n 1000 -c 10 http://localhost:8000/ 2>&1 | tee ab_results/dynamic_gunicorn.txt

echo ""
echo "=== ТЕСТ 4: Динамика через nginx (прокси, без кэша) ==="
ab -n 1000 -c 10 http://localhost:8080/ 2>&1 | tee ab_results/dynamic_proxy_no_cache.txt

echo ""
echo "=== ТЕСТ 5: Динамика через nginx (прокси, с кэшем) ==="
ab -n 1000 -c 10 http://localhost:8080/cached/ 2>&1 | tee ab_results/dynamic_proxy_cache.txt

echo ""
echo "========================================="
echo "Тестирование завершено!"
echo "Результаты сохранены в папку ab_results/"
echo "========================================="

# Вывод краткой статистики
echo ""
echo "📊 Краткая статистика:"
echo "Статика nginx: $(grep "Requests per second" ab_results/static_nginx.txt | cut -d: -f2)"
echo "Статика gunicorn: $(grep "Requests per second" ab_results/static_gunicorn.txt | cut -d: -f2)"
echo "Динамика gunicorn: $(grep "Requests per second" ab_results/dynamic_gunicorn.txt | cut -d: -f2)"
echo "Динамика прокси (без кэша): $(grep "Requests per second" ab_results/dynamic_proxy_no_cache.txt | cut -d: -f2)"
echo "Динамика прокси (с кэшем): $(grep "Requests per second" ab_results/dynamic_proxy_cache.txt | cut -d: -f2)"

# Остановка процессов
pkill -f gunicorn
pkill -f nginx