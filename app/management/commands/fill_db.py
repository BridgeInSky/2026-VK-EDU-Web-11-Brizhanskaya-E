from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from faker import Faker
import random
from app.models import Profile, Tag, Question, Answer

fake = Faker()

class Command(BaseCommand):
    help = 'Fill database with test data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Scale factor (number of users)')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']
        
        users_count = ratio
        questions_count = ratio * 10
        answers_count = ratio * 100
        tags_count = max(ratio, 10)
        
        self.stdout.write(f"Creating {users_count} users...")
        users = []
        for i in range(users_count):
            user = User(
                username=fake.unique.user_name(),
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            user.set_password('password123')
            users.append(user)
        
        User.objects.bulk_create(users, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f"Created {users_count} users"))
        
        self.stdout.write(f"Creating profiles...")
        profiles = [Profile(user_id=user.id) for user in User.objects.all()]
        Profile.objects.bulk_create(profiles, batch_size=1000)
        
        self.stdout.write(f"Creating {tags_count} tags...")
        tags = []
        for i in range(tags_count):
            tags.append(Tag(name=fake.unique.word()))
        Tag.objects.bulk_create(tags, batch_size=1000)
        tags_list = list(Tag.objects.all())
        
        self.stdout.write(f"Creating {questions_count} questions...")
        questions = []
        user_ids = list(User.objects.values_list('id', flat=True))
        
        for i in range(questions_count):
            question = Question(
                title=fake.sentence(nb_words=10)[:200],
                text=fake.paragraph(nb_sentences=5),
                author_id=random.choice(user_ids),
                rating=random.randint(-10, 50)
            )
            questions.append(question)
        
        Question.objects.bulk_create(questions, batch_size=1000)
        
        self.stdout.write(f"Adding tags to questions...")
        questions_list = list(Question.objects.all())
        for question in questions_list:
            random_tags = random.sample(tags_list, k=min(random.randint(1, 5), len(tags_list)))
            question.tags.set(random_tags)
        
        self.stdout.write(f"Creating {answers_count} answers...")
        answers = []
        for i in range(answers_count):
            answer = Answer(
                text=fake.paragraph(nb_sentences=3),
                author_id=random.choice(user_ids),
                question_id=random.choice(questions_list).id,
                rating=random.randint(-5, 30)
            )
            answers.append(answer)
        
        Answer.objects.bulk_create(answers, batch_size=1000)
        
        self.stdout.write(self.style.SUCCESS(
            f"Done! Created: {users_count} users, {tags_count} tags, "
            f"{questions_count} questions, {answers_count} answers"
        ))