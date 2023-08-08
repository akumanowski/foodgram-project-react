"""Модуль управления моделями приложения recipe (Рецепты)."""
from django.conf import settings
from django.db import models
from api.validators import (model_validate_minutes, model_validate_qty,
                            model_validate_slug)
from users.models import FoodgramUser


class Tag(models.Model):
    """Класс управления данными тегов."""
    name = models.CharField(
        max_length=settings.MAX_LENGTH_TAG,
        verbose_name='Названием',
        help_text='Укажите название тега',
        blank=False,
        unique=True
    )
    color = models.CharField(
        max_length=settings.MAX_LENGTH_COLOR,
        verbose_name='Цвет',
        help_text='Укажите цвет тега',
        blank=False,
        unique=True
    )
    slug = models.SlugField(
        max_length=settings.MAX_LENGTH_TAG,
        verbose_name='Тег',
        help_text='Присвойте тегу уникальный slug',
        blank=False,
        validators=[model_validate_slug],
        unique=True
    )

    class Meta:
        default_related_name = 'tags'
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Класс управления справочником ингредиентов."""
    name = models.CharField(
        max_length=settings.MAX_LENGTH_INGREDIENT,
        verbose_name='Названием',
        help_text='Укажите название ингредиента',
        blank=False,
        db_index=True
    )
    measurement_unit = models.CharField(
        max_length=settings.MAX_LENGTH_MEASUREMENT_UNIT,
        blank=False,
        verbose_name='Ед.измерения',
        help_text='Укажите единицу измерения для ингредиента'
    )

    class Meta:
        default_related_name = 'ingredients'
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['id']

        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            ),
        )

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    """Класс управления данными рецепта."""

    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
        blank=False
    )
    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        verbose_name='Названием',
        help_text='Укажите название рецепта',
        blank=False
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=False,
        verbose_name='Картинка',
        help_text='Выберите иллюстрацию для рецепта',
        default=None
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Опишите рецепт',
        blank=False,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты',
        related_name='recipes',
        blank=False
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
        blank=False
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
        help_text='Укажите время приготовления в минутах',
        validators=[model_validate_minutes],
        blank=False
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Дата публикации присваивается автоматически',
        blank=False
    )

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'],
                name='unique_author_name'
            )
        ]

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Класс управления списком ингредиентов в рецепте."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipes',
        verbose_name='Ингредиент',
        help_text='Выберите продукт в качестве ингредиента',
        blank=False
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipes',
        verbose_name='Рецепт',
        help_text='Укажите рецепт для ингредиента',
        blank=False
    )

    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        help_text='Укажите количество продукта',
        validators=[model_validate_qty],
        blank=False
    )

    class Meta:
        default_related_name = 'ingredients_in_recipes'
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        return (
            f'{self.recipe} содержит '
            f'{self.ingredient} {self.amount}'
        )


class Favorite(models.Model):
    """Класс управления данными списка избранного."""

    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='liked',
        verbose_name='Избранные рецепты',
        help_text='Выберите рецепты в качестве избранных'
    )

    class Meta:
        verbose_name = 'Список избранного'
        verbose_name_plural = 'Список избранного'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} выбрал {self.recipe}'


class ShoppingList(models.Model):
    """Класс управления данными списка для покупок."""

    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Покупатель',
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Закупаемые рецепты',
        help_text='Выберите рецепты для закупки'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_list'
            )
        ]

    def __str__(self):
        return f'{self.user} выбрал {self.recipe} для закупки.'
