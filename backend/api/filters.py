from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    """Класс-фильтр для модели Recipe."""
    # Показывать только рецепты, находящиеся в списке избранного.
    is_favorited = filters.BooleanFilter(method='is_favorited_filter')

    # Показывать только рецепты, находящиеся в списке покупок.
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter')

    # Показывать рецепты только автора с указанным id.
    author = filters.NumberFilter(field_name='author__id')

    # Показывать рецепты только с указанными тегами (по slug)
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tag.objects.all())

    # Метод для определения вхождения в список избранного
    def is_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value:
                return queryset.filter(liked__user=user)
        return queryset

    # Метод для определения нахождения в корзине покупок
    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value:
                return queryset.filter(shopping_list__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
        )
