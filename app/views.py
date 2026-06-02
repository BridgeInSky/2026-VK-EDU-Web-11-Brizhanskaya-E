# from django.shortcuts import render, get_object_or_404
# from django.http import Http404
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from .models import Question, Answer

# def paginate(objects_list, request, per_page=10):
#     paginator = Paginator(objects_list, per_page)
#     page_number = request.GET.get('page', 1)
    
#     try:
#         page = paginator.page(page_number)
#     except PageNotAnInteger:
#         page = paginator.page(1)
#     except EmptyPage:
#         page = paginator.page(paginator.num_pages)
    
#     return page

# def index(request):
#     questions = Question.objects.new()
#     page = paginate(questions, request, per_page=10)
#     return render(request, 'index.html', {'page': page, 'questions': page.object_list})

# def hot(request):
#     questions = Question.objects.best()
#     page = paginate(questions, request, per_page=10)
#     return render(request, 'hot.html', {'page': page, 'questions': page.object_list})

# def tag_questions(request, tag_name):
#     questions = Question.objects.by_tag(tag_name)
#     if not questions.exists():
#         raise Http404("Тег не найден")
#     page = paginate(questions, request, per_page=10)
#     return render(request, 'tag.html', {'tag': tag_name, 'page': page, 'questions': page.object_list})

# def question_detail(request, question_id):
#     question = get_object_or_404(Question.objects.select_related('author').prefetch_related('tags'), id=question_id)
#     answers = question.answers.select_related('author')
#     page = paginate(answers, request, per_page=5)
#     return render(request, 'question.html', {'question': question, 'page': page, 'answers': page.object_list})

# def ask(request):
#     return render(request, 'ask.html')

# def login_view(request):
#     return render(request, 'login.html')

# def signup_view(request):
#     return render(request, 'signup.html')

# def profile_view(request):
#     return render(request, 'profile.html')






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
    
    # Популярные теги для сайдбара
    popular_tags = Tag.objects.annotate(
        question_count=models.Count('questions')
    ).order_by('-question_count')[:10]
    
    return render(request, 'index.html', {
        'page': page,
        'popular_tags': popular_tags,
    })

def hot(request):
    """Страница лучших вопросов"""
    questions = Question.objects.best()
    page = paginate(questions, request, per_page=10)
    
    popular_tags = Tag.objects.annotate(
        question_count=models.Count('questions')
    ).order_by('-question_count')[:10]
    
    return render(request, 'hot.html', {
        'page': page,
        'popular_tags': popular_tags,
    })

def tag_questions(request, tag_name):
    """Страница вопросов по тегу"""
    questions = Question.objects.by_tag(tag_name)
    page = paginate(questions, request, per_page=10)
    
    popular_tags = Tag.objects.annotate(
        question_count=models.Count('questions')
    ).order_by('-question_count')[:10]
    
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
    
    popular_tags = Tag.objects.annotate(
        question_count=models.Count('questions')
    ).order_by('-question_count')[:10]
    
    # Форма для ответа (только для авторизованных)
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
    
    popular_tags = Tag.objects.annotate(
        question_count=models.Count('questions')
    ).order_by('-question_count')[:10]
    
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
            
            # Получаем номер страницы, на которой находится новый ответ
            answers_list = question.answers.all()
            paginator = Paginator(answers_list, 5)
            # Находим страницу с новым ответом
            page_num = 1
            for i, page in enumerate(paginator.page_range, 1):
                if answer in paginator.page(page).object_list:
                    page_num = i
                    break
            
            # Редирект с якорем на ответ
            return redirect(f"{reverse('app:question', args=[question.id])}?page={page_num}#answer-{answer.id}")
    else:
        return redirect('app:question', question_id=question.id)
    
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
                
                # Проверка next URL на безопасность
                if next_url:
                    # Разрешаем только относительные URL
                    parsed_url = urlparse(next_url)
                    if not parsed_url.netloc and not parsed_url.scheme:
                        return redirect(next_url)
                return redirect('app:index')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = LoginForm()
    
    popular_tags = Tag.objects.annotate(
        question_count=models.Count('questions')
    ).order_by('-question_count')[:10]
    
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
    
    popular_tags = Tag.objects.annotate(
        question_count=models.Count('questions')
    ).order_by('-question_count')[:10]
    
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
    
    popular_tags = Tag.objects.annotate(
        question_count=models.Count('questions')
    ).order_by('-question_count')[:10]
    
    return render(request, 'profile.html', {
        'form': form,
        'popular_tags': popular_tags,
    })

def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    # Возвращаемся на предыдущую страницу
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))
    return redirect(next_url)

# Добавляем импорт models в начало файла
from django.db import models