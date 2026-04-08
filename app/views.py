from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages

def paginate(objects_list, request, per_page=5):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    
    return page

def generate_questions():
    questions = []
    for i in range(1, 50):
        questions.append({
            'id': i,
            'title': f'Как правильно использовать Bootstrap в Django?',
            'text': f'Подскажите, пожалуйста, как правильно интегрировать Bootstrap в Django проект. Нужно ли копировать файлы в статику или лучше использовать CDN? Какие есть плюсы и минусы у каждого подхода?',
            'answer_count': i * 2 % 15,
            'tags': ['python', 'django', 'javascript', 'html', 'css', 'bootstrap'][:i % 4 + 1],
            'created_at': '2024-01-01',
            'author': f'Пользователь{i}',
            'likes': i * 3 % 100,
        })
    return questions

def index(request):
    questions = generate_questions()
    page = paginate(questions, request)
    return render(request, 'index.html', {
        'page': page, 
        'title': 'Новые вопросы'
    })

def hot(request):
    questions = generate_questions()
    questions.sort(key=lambda x: x['likes'], reverse=True)
    page = paginate(questions, request)
    return render(request, 'index.html', {
        'page': page, 
        'title': 'Лучшие вопросы'
    })

def tag(request, tag_name):
    questions = generate_questions()
    filtered = [q for q in questions if tag_name in q['tags']]
    page = paginate(filtered, request)
    return render(request, 'index.html', {
        'page': page, 
        'title': f'Вопросы с тегом: #{tag_name}'
    })

def question_detail(request, question_id):
    questions = generate_questions()
    question = next((q for q in questions if q['id'] == question_id), None)
    
    if not question:
        return redirect('app:index')
    
    answers = []
    for i in range(1, 25):
        answers.append({
            'id': i,
            'text': f'Ответ номер {i} на вопрос. Здесь подробно расписан ответ на вопрос пользователя.',
            'author': f'Expert{i}',
            'created_at': '2024-01-01',
            'likes': i * 2 % 50,
            'is_correct': i == 3,  # Третий ответ - правильный
        })
    
    page = paginate(answers, request, per_page=3)
    return render(request, 'question.html', {
        'question': question,
        'page': page,
    })

def login_view(request):
    return render(request, 'login.html')

def signup_view(request):
    return render(request, 'signup.html')

def ask_view(request):
    return render(request, 'ask.html')

def profile_view(request):
    return render(request, 'profile.html')