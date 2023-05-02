import json
import os.path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from food.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает данные из JSON-файла в базу данных'

    def handle(self, *args, **options):
        with open(os.path.join(settings.BASE_DIR, 'data', 'ingredients.json'),
                  'r') as jsonfile:
            data = json.load(jsonfile)
            for item in data:
                name = item['name']
                measurement_unit = item['measurement_unit']
                try:
                    Ingredient.objects.create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
                except IntegrityError:
                    self.stdout.write(self.style.WARNING(
                        f"Ingredient '{name}' already exists, skipping."))
