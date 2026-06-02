from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Question, Answer

def paginate(objects_list, request, per_page=10):
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
    questions = Question.objects.new()
    page = paginate(questions, request, per_page=10)
    return render(request, 'index.html', {'page': page, 'questions': page.object_list})

def hot(request):
    questions = Question.objects.best()
    page = paginate(questions, request, per_page=10)
    return render(request, 'hot.html', {'page': page, 'questions': page.object_list})

def tag_questions(request, tag_name):
    questions = Question.objects.by_tag(tag_name)
    if not questions.exists():
        raise Http404("Тег не найден")
    page = paginate(questions, request, per_page=10)
    return render(request, 'tag.html', {'tag': tag_name, 'page': page, 'questions': page.object_list})

def question_detail(request, question_id):
    question = get_object_or_404(Question.objects.select_related('author').prefetch_related('tags'), id=question_id)
    answers = question.answers.select_related('author')
    page = paginate(answers, request, per_page=5)
    return render(request, 'question.html', {'question': question, 'page': page, 'answers': page.object_list})

def ask(request):
    return render(request, 'ask.html')

def login_view(request):
    return render(request, 'login.html')

def signup_view(request):
    return render(request, 'signup.html')

def profile_view(request):
    return render(request, 'profile.html')