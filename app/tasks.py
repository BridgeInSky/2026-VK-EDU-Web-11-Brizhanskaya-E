from celery import shared_task
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from datetime import timedelta
from .models import Tag, User, Question, Answer
import requests
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def update_popular_tags():
    """Обновляет кеш популярных тегов"""
    three_months_ago = timezone.now() - timedelta(days=90)
    
    popular_tags = list(Tag.objects.filter(
        questions__created_at__gte=three_months_ago
    ).annotate(
        question_count=models.Count('questions')
    ).order_by('-question_count')[:10].values('name', 'question_count'))
    
    cache.set('popular_tags', popular_tags, 60 * 10)
    return popular_tags


@shared_task
def update_best_members():
    """Обновляет кеш лучших пользователей"""
    one_week_ago = timezone.now() - timedelta(days=7)
    
    best_users = list(User.objects.filter(
        models.Q(questions__created_at__gte=one_week_ago) |
        models.Q(answers__created_at__gte=one_week_ago)
    ).annotate(
        total_rating=models.Sum('questions__rating') + models.Sum('answers__rating')
    ).filter(total_rating__isnull=False).order_by('-total_rating')[:10].values('id', 'username', 'total_rating'))
    
    cache.set('best_members', best_users, 60 * 10)
    return best_users


@shared_task
def send_answer_notification(answer_id, question_author_email, question_title, question_author_username):
    """Отправляет email уведомление"""
    try:
        answer = Answer.objects.get(id=answer_id)
        
        subject = f'Новый ответ на ваш вопрос "{question_title}"'
        message = f"""
Здравствуйте, {question_author_username}!

Пользователь {answer.author.username} ответил на ваш вопрос "{question_title}".

Текст ответа:
{answer.text[:300]}

Посмотреть ответ: http://localhost:8000/question/{answer.question.id}/#answer-{answer.id}

С уважением,
Команда AskMe
"""
        send_mail(
            subject=subject,
            message=message.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[question_author_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

@shared_task
def send_centrifugo_notification(question_id, answer_text, answer_author, answer_id):
    """Отправляет уведомление в Centrifugo о новом ответе"""
    import requests
    from django.conf import settings
    import os
    
    # Принудительно берём ключ
    api_key = os.getenv('CENTRIFUGO_API_KEY', settings.CENTRIFUGO_API_KEY)
    
    url = f"{settings.CENTRIFUGO_URL}/api/publish"
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    data = {
        "channel": f"questions:{question_id}",
        "data": {
            "type": "new_answer",
            "answer_id": answer_id,
            "answer_preview": answer_text[:200],
            "author": answer_author,
            "timestamp": str(timezone.now())
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=5)
        print(f"Centrifugo response status: {response.status_code}")
        print(f"Centrifugo response body: {response.text}")
        if response.status_code == 200:
            print(f"✅ Centrifugo sent for question {question_id}")
            return True
        else:
            print(f"❌ Centrifugo error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Centrifugo error: {e}")
        return False

# @shared_task
# def send_centrifugo_notification(question_id, answer_text, answer_author, answer_id):
#     """Отправляет уведомление в Centrifugo о новом ответе"""
#     from django.conf import settings
#     import requests
    
#     url = f"{settings.CENTRIFUGO_URL}/api/publish"
#     headers = {
#         'X-API-Key': settings.CENTRIFUGO_API_KEY,
#         'Content-Type': 'application/json'
#     }
#     data = {
#         "channel": f"questions:{question_id}",
#         "data": {
#             "type": "new_answer",
#             "answer_id": answer_id,
#             "answer_preview": answer_text[:200],
#             "author": answer_author,
#             "timestamp": str(timezone.now())
#         }
#     }
    
#     try:
#         response = requests.post(url, json=data, headers=headers, timeout=5)
#         print(f"Centrifugo response status: {response.status_code}")
#         print(f"Centrifugo response body: {response.text}")
#         if response.status_code == 200:
#             print(f"✅ Centrifugo sent for question {question_id}")
#             return True
#         else:
#             print(f"❌ Centrifugo error: {response.status_code} - {response.text}")
#             return False
#     except Exception as e:
#         print(f"❌ Centrifugo error: {e}")
#         return False

# @shared_task
# def send_centrifugo_notification(question_id, answer_text, answer_author, answer_id):
#     print(f"🔔 Sending to Centrifugo: question {question_id}, answer {answer_id}")
#     """Отправляет уведомление в Centrifugo"""
#     url = f"http://localhost:8001/api/publish"
#     headers = {
#         'Content-Type': 'application/json'
#     }
#     data = {
#         "channel": f"questions:{question_id}",
#         "data": {
#             "type": "new_answer",
#             "answer_id": answer_id,
#             "answer_preview": answer_text[:200],
#             "author": answer_author,
#             "timestamp": str(timezone.now())
#         }
#     }
    
#     try:
#         response = requests.post(url, json=data, headers=headers, timeout=5)
#         if response.status_code == 200:
#             print(f"✅ Centrifugo sent for question {question_id}")
#             return True
#         else:
#             print(f"❌ Centrifugo error: {response.status_code} - {response.text}")
#             return False
#     except Exception as e:
#         print(f"❌ Centrifugo error: {e}")
#         return False