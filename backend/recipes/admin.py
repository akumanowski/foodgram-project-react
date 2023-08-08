from django.contrib import admin, messages

from . import models
from .csv_import import run_import_csv


class BaseModelAdmin(admin.ModelAdmin):
    """Базовые настройки админки для моделей."""
    empty_value_display = '-пусто-'


@admin.register(models.Tag)
class TagAdmin(BaseModelAdmin):
    """Настройки админки для тегов."""
    list_display = ('id', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')


@admin.register(models.Ingredient)
class IngredientAdmin(BaseModelAdmin):
    """Настройки админки для ингредиентов."""
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    actions = ['import_data']

    @admin.action(
        description='Выполнить импорт данных из файла ingredients.csv'
    )
    def import_data(self, request, datasource):
        results = run_import_csv()
        status = messages.ERROR
        false_message = f'{results["false"]} записей заполнены некорректно'
        dub_message = f'{results["dub"]} записей дублируются'
        sum_record = results["true"] + results["false"] + results["dub"]
        if results['false'] + results['dub'] == 0:
            message = (f'{results["true"]} новых ингредиентов '
                       f'было загружено в базу данных Foodgram.')
            status = messages.SUCCESS
        elif results['true'] > 0:
            message = (f'В процессе загрузки {sum_record} новых '
                       f'ингредиентов: {false_message}, {dub_message}.')
        else:
            message = (f'Не удалось загрузить данные: '
                       f'{false_message}, {dub_message}.')
        self.message_user(
            request,
            message,
            status
        )


@admin.register(models.Recipe)
class RecipeAdmin(BaseModelAdmin):
    """Настройки админки для рецептов."""
    list_display = ('id', 'name', 'author')
    list_display_links = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('tags',)
    list_filter = ('author', 'name', 'tags')
    readonly_fields = ('count_of_favorites',)

    def count_of_favorites(self, obj):
        return obj.liked.all().count()

    count_of_favorites.short_description = 'Счётчик избранного'


@admin.register(models.IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Настройки админки для ингредиентов в рецепте."""
    list_display = ('id', 'ingredient', 'amount',)
    list_filter = ('ingredient',)


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Настройки админки для избранных рецептов."""
    list_display = ('id', 'user', 'recipe')


@admin.register(models.ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Настройки админки для списка покупок."""
    list_display = ('id', 'recipe', 'user')
