# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 2
worker_class = "sync"
timeout = 30
accesslog = "-"
errorlog = "-"
loglevel = "info"
