from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    search_fields = ['username', 'email']

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'rating']
    list_filter = ['created_at', 'tags']
    search_fields = ['title', 'author__username']
    raw_id_fields = ['author']

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'author', 'created_at', 'is_correct']
    list_filter = ['is_correct', 'created_at']
    search_fields = ['text', 'author__username']
    raw_id_fields = ['question', 'author']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'value']
    list_filter = ['value']
    raw_id_fields = ['user', 'question']

@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'answer', 'value']
    list_filter = ['value']
    raw_id_fields = ['user', 'answer']