from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Question, Answer, Tag, Profile

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Имя пользователя',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите username'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'})
    )

class SignupForm(UserCreationForm):
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.ru'})
    )
    username = forms.CharField(
        label='Имя пользователя',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите username'})
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}),
        help_text='Пароль должен содержать не менее 8 символов'
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите пароль'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Создаем профиль для пользователя
            Profile.objects.create(user=user)
        return user

class ProfileForm(forms.ModelForm):
    username = forms.CharField(
        label='Имя пользователя',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    avatar = forms.ImageField(
        label='Аватар',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Profile
        fields = ('avatar',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['username'].initial = self.user.username
            self.fields['email'].initial = self.user.email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if self.user and username != self.user.username:
            if User.objects.filter(username=username).exists():
                raise ValidationError('Пользователь с таким именем уже существует')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user and email != self.user.email:
            if User.objects.filter(email=email).exists():
                raise ValidationError('Пользователь с таким email уже существует')
        return email

    def save(self, commit=True):
        if self.user:
            self.user.username = self.cleaned_data['username']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        
        profile = super().save(commit=False)
        profile.user = self.user
        if commit:
            profile.save()
        return profile

class AskForm(forms.ModelForm):
    tags = forms.CharField(
        label='Теги',
        required=True,
        help_text='Введите теги через пробел (например: python django web)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'python django javascript'})
    )

    class Meta:
        model = Question
        fields = ('title', 'text')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Какой у вас вопрос?'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Подробно опишите проблему...'}),
        }
        labels = {
            'title': 'Заголовок',
            'text': 'Текст вопроса',
        }
        help_texts = {
            'title': 'Максимум 200 символов',
            'text': 'Подробно опишите вашу проблему',
        }

    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags', '')
        tags_list = [tag.strip().lower() for tag in tags_str.split() if tag.strip()]
        if not tags_list:
            raise ValidationError('Укажите хотя бы один тег')
        if len(tags_list) > 5:
            raise ValidationError('Не более 5 тегов на вопрос')
        return tags_list

    def save(self, author, commit=True):
        question = super().save(commit=False)
        question.author = author
        if commit:
            question.save()
            # Обработка тегов
            tags_list = self.cleaned_data['tags']
            for tag_name in tags_list:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                question.tags.add(tag)
            question.save()
        return question

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Напишите ваш ответ...'
            }),
        }
        labels = {
            'text': 'Ваш ответ',
        }

    def save(self, question, author, commit=True):
        answer = super().save(commit=False)
        answer.question = question
        answer.author = author
        if commit:
            answer.save()
        return answer