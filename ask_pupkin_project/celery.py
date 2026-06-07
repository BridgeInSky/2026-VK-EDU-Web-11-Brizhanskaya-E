import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ask_pupkin_project.settings')

app = Celery('ask_pupkin_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Настройки периодических задач
app.conf.beat_schedule = {
    'update-popular-tags': {
        'task': 'app.tasks.update_popular_tags',
        'schedule': crontab(minute='*/10'),  # Каждые 10 минут
    },
    'update-best-members': {
        'task': 'app.tasks.update_best_members',
        'schedule': crontab(minute='*/10'),  # Каждые 10 минут
    },
}