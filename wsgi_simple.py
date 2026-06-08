#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.parse
from html import escape

def application(environ, start_response):
    """
    Простое WSGI приложение, которое выводит GET и POST параметры.
    Запускается на localhost:8081
    """
    
    # Статус ответа
    status = '200 OK'
    
    # Заголовки
    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Cache-Control', 'no-cache, no-store, must-revalidate'),
    ]
    
    # Получаем метод запроса
    method = environ.get('REQUEST_METHOD', 'GET')
    
    # Получаем GET параметры
    query_string = environ.get('QUERY_STRING', '')
    get_params = urllib.parse.parse_qs(query_string)
    
    # Получаем POST параметры (читаем тело запроса)
    post_params = {}
    if method == 'POST':
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            if content_length > 0:
                request_body = environ['wsgi.input'].read(content_length).decode('utf-8')
                post_params = urllib.parse.parse_qs(request_body)
        except:
            post_params = {}
    
    # Получаем путь запроса
    path = environ.get('PATH_INFO', '/')
    
    # Формируем HTML ответ
    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WSGI Simple App</title>
        <style>
            body {{
                font-family: 'Courier New', monospace;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #1e1e1e;
                color: #d4d4d4;
            }}
            h1 {{ color: #4ec9b0; }}
            h2 {{ color: #ce9178; margin-top: 30px; }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: #252526;
            }}
            th, td {{
                border: 1px solid #3e3e42;
                padding: 8px 12px;
                text-align: left;
            }}
            th {{ background: #2d2d30; color: #9cdcfe; }}
            td {{ color: #d4d4d4; }}
            .info {{ background: #2d2d30; padding: 10px; border-radius: 5px; margin: 20px 0; }}
            code {{ background: #1e1e1e; padding: 2px 5px; border-radius: 3px; color: #ce9178; }}
            hr {{ border-color: #3e3e42; }}
            form {{ background: #252526; padding: 15px; border-radius: 5px; }}
            input, button {{
                padding: 8px;
                margin: 5px;
                background: #3e3e42;
                border: 1px solid #4ec9b0;
                color: #d4d4d4;
            }}
            button:hover {{ background: #4ec9b0; color: #1e1e1e; cursor: pointer; }}
        </style>
    </head>
    <body>
        <h1>📋 WSGI Simple Application</h1>
        <div class="info">
            <strong>📍 Путь запроса:</strong> <code>{path}</code><br>
            <strong>🔄 Метод запроса:</strong> <code>{method}</code>
        </div>
        
        <h2>📥 GET параметры</h2>
        {format_params(get_params)}
        
        <h2>📦 POST параметры</h2>
        {format_params(post_params)}
        
        <hr>
        
        <h2>📤 Тестовая форма</h2>
        <form method="GET" style="margin-bottom: 20px;">
            <h3>GET запрос</h3>
            <input type="text" name="name" placeholder="Имя" value="Иван">
            <input type="text" name="email" placeholder="Email" value="ivan@example.com">
            <button type="submit">Отправить GET</button>
        </form>
        
        <form method="POST">
            <h3>POST запрос</h3>
            <input type="text" name="username" placeholder="Логин" value="alex_master">
            <input type="text" name="message" placeholder="Сообщение" value="Привет, мир!">
            <button type="submit">Отправить POST</button>
        </form>
        
        <hr>
        <div class="info">
            <strong>🔧 Запуск:</strong> gunicorn wsgi_simple:application -b localhost:8081 --workers=2<br>
            <strong>📖 Документация:</strong> WSGI (Web Server Gateway Interface)
        </div>
    </body>
    </html>
    """
    
    # Функция для форматирования параметров
    def format_params(params):
        if not params:
            return "<p>📭 Параметры отсутствуют</p>"
        
        html_table = "<table>"
        html_table += "<tr><th>Ключ</th><th>Значение</th></tr>"
        for key, values in params.items():
            html_table += f"<tr><td><code>{escape(key)}</code></td><td>{escape(', '.join(values))}</td></tr>"
        html_table += "</table>"
        return html_table
    
    start_response(status, headers)
    return [html.encode('utf-8')]

# Для запуска вручную
if __name__ == '__main__':
    print("Запуск простого WSGI сервера...")
    print("gunicorn wsgi_simple:application -b localhost:8081 --workers=2")
    print("Откройте http://localhost:8081")