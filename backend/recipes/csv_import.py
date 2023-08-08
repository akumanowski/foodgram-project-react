"""
Модуль импорта ингредиентов из файла CSV.
"""
import csv
import os
from .models import Ingredient
from foodgram.settings import FOOD_DATA_ROOT

FILENAME = 'ingredients.csv'


def run_import_csv():
    """Загрузка CSV файла"""
    with open(os.path.join(FOOD_DATA_ROOT, FILENAME), encoding='utf-8') as r_file:
        # Создаем объект reader, указываем символ-разделитель ","
        file_reader = csv.reader(r_file, delimiter=",")
        # Счетчики для подсчета количества строк
        true_count = 0  # корректные данные
        false_count = 0  # данные с ошибками
        dub_count = 0  # повторяющиеся данные
        # Считывание данных из CSV файла
        for row in file_reader:
            # Строки данных
            if "" in row:
                false_count += 1
            else:
                if Ingredient.objects.filter(
                        name=row[0],
                        measurement_unit=row[1]
                ).exists():
                    # Данные уже присутствуют в списке ингредиентов
                    dub_count += 1
                else:
                    Ingredient.objects.create(
                        name=row[0],
                        measurement_unit=row[1]).save()
                    true_count += 1
    return {'true': true_count, 'false': false_count, 'dub': dub_count}
