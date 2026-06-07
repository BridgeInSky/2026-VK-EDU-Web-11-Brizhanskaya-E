import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike
from faker import Faker

fake_ru = Faker('ru_RU')  # Для русского контента
fake_en = Faker('en_US')  # Для английских никнеймов


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными (никнеймы на английском, вопросы на русском)'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Коэффициент заполнения')

    def handle(self, *args, **options):
        ratio = options['ratio']
        
        self.stdout.write('Начинаем заполнение БД...')
        self.stdout.write('  - Никнеймы пользователей: английские')
        self.stdout.write('  - Вопросы и ответы: русские')
        
        # 1. Создаем теги (смешанные, но в основном английские для удобства поиска)
        tags_list = [
            'python', 'django', 'javascript', 'html', 'css', 
            'git', 'docker', 'postgresql', 'redis', 'celery',
            'linux', 'windows', 'macos', 'vscode', 'pycharm',
            'flask', 'fastapi', 'sql', 'nosql', 'mongodb',
            'react', 'vue', 'angular', 'typescript', 'php',
            'java', 'kotlin', 'swift', 'go', 'rust'
        ]
        tags = []
        for tag_name in tags_list[:min(ratio, len(tags_list))]:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            tags.append(tag)
            if created:
                self.stdout.write(f'  Создан тег: {tag_name}')
        
        # 2. Создаем пользователей (английские имена + русские имена для отображения)
        users = []
        for i in range(ratio):
            # Генерируем английский username
            username = fake_en.user_name() + f"_{i}" if i > 0 else fake_en.user_name()
            
            # Русское имя и фамилия для отображения (first_name, last_name)
            first_name = fake_ru.first_name_male() if i % 2 == 0 else fake_ru.first_name_female()
            last_name = fake_ru.last_name()
            
            email = f"{username}@example.com"
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password='testpass123'
            )
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            
            # Создаем профиль
            Profile.objects.get_or_create(user=user)
            users.append(user)
            
            if i % 100 == 0:
                self.stdout.write(f'  Создано пользователей: {i}')
        
        self.stdout.write(f'  Всего создано пользователей: {len(users)}')
        
        # 3. Создаем вопросы (русские)
        questions = []
        questions_count = ratio * 10
        for i in range(questions_count):
            author = random.choice(users)
            title = fake_ru.sentence(nb_words=random.randint(5, 12))
            text = fake_ru.paragraph(nb_sentences=random.randint(3, 8))
            
            question = Question.objects.create(
                title=title.rstrip('.'),
                text=text,
                author=author,
                rating=random.randint(-10, 50)
            )
            
            # Добавляем теги
            num_tags = random.randint(1, 4)
            question.tags.add(*random.sample(tags, min(num_tags, len(tags))))
            questions.append(question)
            
            if i % 100 == 0:
                self.stdout.write(f'  Создано вопросов: {i}')
        
        self.stdout.write(f'  Всего создано вопросов: {len(questions)}')
        
        # 4. Создаем ответы (русские)
        answers = []
        answers_count = ratio * 100
        for i in range(answers_count):
            question = random.choice(questions)
            author = random.choice(users)
            text = fake_ru.paragraph(nb_sentences=random.randint(2, 5))
            
            answer = Answer.objects.create(
                text=text,
                author=author,
                question=question,
                rating=random.randint(-5, 30)
            )
            answers.append(answer)
            
            if i % 500 == 0:
                self.stdout.write(f'  Создано ответов: {i}')
        
        self.stdout.write(f'  Всего создано ответов: {len(answers)}')
        
        # 5. Создаем лайки вопросов
        likes_count = ratio * 100
        for i in range(likes_count):
            user = random.choice(users)
            question = random.choice(questions)
            value = random.choice([1, -1])
            
            try:
                QuestionLike.objects.create(user=user, question=question, value=value)
                question.rating += value
                question.save()
            except:
                pass
            
            if i % 500 == 0:
                self.stdout.write(f'  Создано лайков вопросов: {i}')
        
        # 6. Создаем лайки ответов
        for i in range(likes_count):
            user = random.choice(users)
            answer = random.choice(answers)
            value = random.choice([1, -1])
            
            try:
                AnswerLike.objects.create(user=user, answer=answer, value=value)
                answer.rating += value
                answer.save()
            except:
                pass
            
            if i % 500 == 0:
                self.stdout.write(f'  Создано лайков ответов: {i}')
        
        # 7. Отмечаем несколько правильных ответов
        for question in questions[:questions_count // 10]:
            question_answers = question.answers.all()
            if question_answers.exists():
                correct_answer = random.choice(question_answers)
                correct_answer.is_correct = True
                correct_answer.save()
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ База данных успешно заполнена!\n'
            f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
            f'📊 Статистика:\n'
            f'  👥 Пользователей: {len(users)}\n'
            f'  ❓ Вопросов: {len(questions)}\n'
            f'  💬 Ответов: {len(answers)}\n'
            f'  🏷️ Тегов: {len(tags)}\n'
            f'  👍 Лайков вопросов: {likes_count}\n'
            f'  👎 Лайков ответов: {likes_count}\n'
            f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
            f'✨ Данные сгенерированы с:\n'
            f'  • Никнеймы: английские (Faker en_US)\n'
            f'  • Имена/фамилии: русские\n'
            f'  • Вопросы/ответы: русские (Faker ru_RU)\n'
            f'  • Теги: английские (для удобства поиска)'
        ))