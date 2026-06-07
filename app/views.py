import jwt
import json
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from urllib.parse import urlparse, urlunparse

from .models import Question, Answer, Tag
from .forms import LoginForm, SignupForm, ProfileForm, AskForm, AnswerForm

from django.core.cache import cache
from .tasks import update_popular_tags, update_best_members, send_answer_notification, send_centrifugo_notification

from django.db.models import Q

def paginate(objects_list, request, per_page=10):
    """Функция пагинации"""
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    
    return page

def index(request):
    """Главная страница - список новых вопросов"""
    questions = Question.objects.new()
    page = paginate(questions, request, per_page=10)
    
    popular_tags = cache.get('popular_tags')
    if popular_tags is None:
        popular_tags = update_popular_tags()
    
    return render(request, 'index.html', {
        'page': page,
        'popular_tags': popular_tags,
    })

def hot(request):
    """Страница лучших вопросов"""
    questions = Question.objects.best()
    page = paginate(questions, request, per_page=10)
    
    popular_tags = cache.get('popular_tags')
    if popular_tags is None:
        popular_tags = update_popular_tags()
    
    return render(request, 'hot.html', {
        'page': page,
        'popular_tags': popular_tags,
    })

def tag_questions(request, tag_name):
    """Страница вопросов по тегу"""
    questions = Question.objects.by_tag(tag_name)
    page = paginate(questions, request, per_page=10)
    
    popular_tags = cache.get('popular_tags')
    if popular_tags is None:
        popular_tags = update_popular_tags()
    
    return render(request, 'tag.html', {
        'page': page,
        'tag_name': tag_name,
        'popular_tags': popular_tags,
    })

def question_detail(request, question_id):
    """Страница вопроса с ответами"""
    question = get_object_or_404(Question, id=question_id)
    answers = question.answers.all()
    page = paginate(answers, request, per_page=5)
    
    popular_tags = cache.get('popular_tags')
    if popular_tags is None:
        popular_tags = update_popular_tags()
    
    answer_form = AnswerForm() if request.user.is_authenticated else None
    
    return render(request, 'question.html', {
        'question': question,
        'page': page,
        'popular_tags': popular_tags,
        'answer_form': answer_form,
    })

@login_required
def ask(request):
    """Страница создания вопроса"""
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save(author=request.user)
            messages.success(request, 'Вопрос успешно создан!')
            return redirect('app:question', question_id=question.id)
    else:
        form = AskForm()
    
    popular_tags = cache.get('popular_tags')
    if popular_tags is None:
        popular_tags = update_popular_tags()
    
    return render(request, 'ask.html', {
        'form': form,
        'popular_tags': popular_tags,
    })

@login_required
def answer_add(request, question_id):
    """Добавление ответа на вопрос"""
    question = get_object_or_404(Question, id=question_id)
    
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(question=question, author=request.user)
            messages.success(request, 'Ответ успешно добавлен!')
            
            if question.author != request.user and question.author.email:
                send_answer_notification.delay(
                    answer.id,
                    question.author.email,
                    question.title,
                    question.author.username
                )
            
            send_centrifugo_notification.delay(
                question.id,
                answer.text,
                request.user.username,
                answer.id
            )
            
            return redirect(f"{reverse('app:question', args=[question.id])}#answer-{answer.id}")
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    
    return redirect('app:question', question_id=question.id)

def login_view(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect('app:index')
    
    next_url = request.GET.get('next', '')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                
                if next_url:
                    parsed_url = urlparse(next_url)
                    if not parsed_url.netloc and not parsed_url.scheme:
                        return redirect(next_url)
                return redirect('app:index')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = LoginForm()
    
    popular_tags = cache.get('popular_tags')
    if popular_tags is None:
        popular_tags = update_popular_tags()
    
    return render(request, 'login.html', {
        'form': form,
        'next': next_url,
        'popular_tags': popular_tags,
    })

def signup_view(request):
    """Регистрация пользователя"""
    if request.user.is_authenticated:
        return redirect('app:index')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Регистрация прошла успешно! Добро пожаловать, {user.username}!')
            return redirect('app:index')
    else:
        form = SignupForm()
    
    popular_tags = cache.get('popular_tags')
    if popular_tags is None:
        popular_tags = update_popular_tags()
    
    return render(request, 'signup.html', {
        'form': form,
        'popular_tags': popular_tags,
    })

@login_required
def profile_view(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, user=request.user, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('app:profile')
    else:
        form = ProfileForm(user=request.user, instance=request.user.profile)
    
    popular_tags = cache.get('popular_tags')
    if popular_tags is None:
        popular_tags = update_popular_tags()
    
    return render(request, 'profile.html', {
        'form': form,
        'popular_tags': popular_tags,
    })

def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))
    return redirect(next_url)

from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import QuestionLike, AnswerLike

@login_required
@require_POST
def question_like(request, question_id):
    """Лайк/дизлайк вопроса (AJAX)"""
    try:
        question = get_object_or_404(Question, id=question_id)
        
        # Пробуем получить данные из JSON или из POST
        try:
            data = json.loads(request.body)
            action = data.get('action')
        except:
            action = request.POST.get('action')
        
        if action not in ['like', 'dislike']:
            return JsonResponse({'error': 'Неверное действие'}, status=400)
        
        existing_like = QuestionLike.objects.filter(
            user=request.user, 
            question=question
        ).first()
        
        new_value = 1 if action == 'like' else -1
        
        if existing_like:
            if existing_like.value == new_value:
                existing_like.delete()
                new_rating = question.rating - new_value
                question.rating = new_rating
                question.save()
                return JsonResponse({
                    'status': 'removed',
                    'new_rating': new_rating,
                    'user_vote': None
                })
            else:
                old_value = existing_like.value
                existing_like.value = new_value
                existing_like.save()
                new_rating = question.rating - old_value + new_value
                question.rating = new_rating
                question.save()
                return JsonResponse({
                    'status': 'changed',
                    'new_rating': new_rating,
                    'user_vote': new_value
                })
        else:
            QuestionLike.objects.create(
                user=request.user,
                question=question,
                value=new_value
            )
            new_rating = question.rating + new_value
            question.rating = new_rating
            question.save()
            return JsonResponse({
                'status': 'added',
                'new_rating': new_rating,
                'user_vote': new_value
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_POST
def answer_like(request, answer_id):
    """Лайк/дизлайк ответа (AJAX)"""
    try:
        answer = get_object_or_404(Answer, id=answer_id)
        
        try:
            data = json.loads(request.body)
            action = data.get('action')
        except:
            action = request.POST.get('action')
        
        if action not in ['like', 'dislike']:
            return JsonResponse({'error': 'Неверное действие'}, status=400)
        
        existing_like = AnswerLike.objects.filter(
            user=request.user, 
            answer=answer
        ).first()
        
        new_value = 1 if action == 'like' else -1
        
        if existing_like:
            if existing_like.value == new_value:
                existing_like.delete()
                new_rating = answer.rating - new_value
                answer.rating = new_rating
                answer.save()
                return JsonResponse({
                    'status': 'removed',
                    'new_rating': new_rating,
                    'user_vote': None
                })
            else:
                old_value = existing_like.value
                existing_like.value = new_value
                existing_like.save()
                new_rating = answer.rating - old_value + new_value
                answer.rating = new_rating
                answer.save()
                return JsonResponse({
                    'status': 'changed',
                    'new_rating': new_rating,
                    'user_vote': new_value
                })
        else:
            AnswerLike.objects.create(
                user=request.user,
                answer=answer,
                value=new_value
            )
            new_rating = answer.rating + new_value
            answer.rating = new_rating
            answer.save()
            return JsonResponse({
                'status': 'added',
                'new_rating': new_rating,
                'user_vote': new_value
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_POST
def mark_correct(request, answer_id):
    """Отметка правильного ответа (только автор вопроса)"""
    try:
        answer = get_object_or_404(Answer, id=answer_id)
        question = answer.question
        
        if question.author != request.user:
            return JsonResponse({'error': 'Только автор вопроса может отмечать правильный ответ'}, status=403)
        
        if answer.is_correct:
            answer.is_correct = False
            answer.save()
            return JsonResponse({
                'status': 'unmarked',
                'is_correct': False
            })
        else:
            question.answers.update(is_correct=False)
            answer.is_correct = True
            answer.save()
            return JsonResponse({
                'status': 'marked',
                'is_correct': True
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ========== ПОЛНОТЕКСТОВЫЙ ПОИСК (одно определение) ==========
from django.contrib.postgres.search import SearchVector, SearchQuery

def search_api(request):
    """API для полнотекстового поиска вопросов"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    questions = Question.objects.annotate(
        search=SearchVector('title', 'text')
    ).filter(search=SearchQuery(query))[:10]
    
    results = []
    for q in questions:
        preview = q.text[:150]
        if query.lower() in preview.lower():
            index = preview.lower().find(query.lower())
            start = max(0, index - 30)
            end = min(len(preview), index + 70)
            preview = '...' + preview[start:end] + '...'
        else:
            preview = preview[:100] + '...'
        
        results.append({
            'id': q.id,
            'title': q.title,
            'preview': preview,
        })
    
    return JsonResponse({'results': results})

@require_http_methods(["GET"])
def get_centrifugo_token(request):
    """Возвращает токен для подключения к Centrifugo"""
    from datetime import datetime
    
    # Для client_insecure токен не нужен, но вернём пустой
    return JsonResponse({'token': ''})