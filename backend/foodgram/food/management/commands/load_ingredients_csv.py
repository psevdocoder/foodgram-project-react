import csv
import os.path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from food.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает данные из CSV-файла в базу данных'

    def handle(self, *args, **options):
        with open(os.path.join(settings.BASE_DIR, 'data', 'ingredients.csv'),
                  'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for name, measurement_unit in reader:
                try:
                    Ingredient.objects.create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
                except IntegrityError:
                    self.stdout.write(self.style.WARNING(
                        f"Ingredient '{name}' already exists, skipping."))
