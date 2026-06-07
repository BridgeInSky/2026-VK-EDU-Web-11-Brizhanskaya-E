from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    # Основные страницы
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('question/<int:question_id>/', views.question_detail, name='question'),
    path('ask/', views.ask, name='ask'),
    path('tag/<str:tag_name>/', views.tag_questions, name='tag'),
    
    # Аутентификация
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Действия с вопросами и ответами
    path('answer/<int:question_id>/', views.answer_add, name='answer_add'),
    
    # API для AJAX
    path('api/question-like/<int:question_id>/', views.question_like, name='question_like'),
    path('api/answer-like/<int:answer_id>/', views.answer_like, name='answer_like'),
    path('api/mark-correct/<int:answer_id>/', views.mark_correct, name='mark_correct'),
    path('api/search/', views.search_api, name='search_api'),
    
    # Centrifugo token
    path('api/centrifugo-token/', views.get_centrifugo_token, name='centrifugo_token'),
]