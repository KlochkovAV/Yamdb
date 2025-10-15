import csv

from django.apps import apps
from django.core.management import BaseCommand

from reviews.models import Category, User


class Command(BaseCommand):
    """Импорт данных из CSV-файлов в указанные модели."""

    FILES_MODELS = {
        'category': 'reviews.Category',
        'genre': 'reviews.Genre',
        'titles': 'reviews.Title',
        'users': 'users.User',
        'review': 'reviews.Review',
        'comments': 'reviews.Comment',
    }

    def handle(self, *args, **options):
        for filename, model_path in self.FILES_MODELS.items():
            model = apps.get_model(model_path)
            file_path = f'static/data/{filename}.csv'

            if model.objects.exists():
                self.stdout.write(
                    self.style.WARNING(
                        f'Данные для {model.__name__} уже существуют.'
                    )
                )
                continue

            with open(file_path, encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                objects = []
                for row in reader:
                    if 'id' in row:
                        row['id'] = int(row['id'])
                    if 'category' in row:
                        row['category'] = Category.objects.get(
                            id=row['category']
                        )
                    if 'author' in row:
                        row['author'] = User.objects.get(
                            id=row['author']
                        )
                    objects.append(model(**row))

                model.objects.bulk_create(objects, ignore_conflicts=True)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Записи успешно загружены в {model.__name__}.'
                    )
                )
