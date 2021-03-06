import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Update database'

    def handle(self, *args, **options):
        with open('ingredients.csv', encoding='utf-8') as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                title, dimension = row
                if i:
                    Ingredient.objects.get_or_create(
                        title=title,
                        dimension=dimension,
                    )
