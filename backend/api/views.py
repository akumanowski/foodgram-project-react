from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated, AllowAny,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Tag, Ingredient, Recipe, IngredientInRecipe,
                            ShoppingList, Favorite)
from users.models import FoodgramUser, Subscription
from .filters import RecipeFilter
from .pagination import FoodgramPaginator
from .permissions import RecipePermission
from .serializers import (TagSerializer, IngredientSerializer,
                          SubscriptionSerializer, RecipeChangeSerializer,
                          RecipeReadSerializer, FoodgramUserSerializer,
                          FoodgramUserCreateSerializer,
                          FavoriteSerializer, ShoppingListSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс-вьюсет для модели Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс-вьюсет для модели Ingredient."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Класс-вьюсет для модели Recipe."""
    http_method_names = ['get', 'post', 'patch', 'create', 'delete']
    queryset = Recipe.objects.all()
    permission_classes = (RecipePermission,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = FoodgramPaginator

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeChangeSerializer
        return RecipeReadSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    http_method_names = ['post', 'delete']
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        recipe_id = kwargs.get("id", None)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = request.user
        get_object_or_404(Favorite, user_id=user.id,
                          recipe_id=recipe.id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingListViewSet(viewsets.ModelViewSet):
    """Вьюсет для добавления и удаления рецептов в корзины покупок."""
    http_method_names = ['get', 'post', 'delete']
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer
    permission_classes = [IsAuthenticated, ]

    def delete(self, request, *args, **kwargs):
        recipe_id = kwargs.get("id", None)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = request.user
        get_object_or_404(ShoppingList, user_id=user.id,
                          recipe_id=recipe.id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shopping_cart = (
            ShoppingList.objects.filter(
                user=self.request.user
            )
        )
        recipes = [item.recipe.id for item in shopping_cart]
        shopping_list = IngredientInRecipe.objects.filter(
            recipe__in=recipes
        ).values(
            'ingredient'
        ).annotate(
            amount=Sum('amount')
        ).order_by('ingredient__name')

        shopping_list_text = 'Список покупок с сайта Foodgram:\n\n'
        for item in shopping_list:
            ingredient = Ingredient.objects.get(pk=item['ingredient'])
            amount = item['amount']
            shopping_list_text += (
                f'{ingredient.name}, {amount} '
                f'{ingredient.measurement_unit}\n'
            )

        response = HttpResponse(shopping_list_text, content_type="text/plain")
        filename = 'shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class FoodgramUserViewSet(UserViewSet):
    """Класс-вьюсет для модели FoodgramUser."""
    queryset = FoodgramUser.objects.all()
    pagination_class = FoodgramPaginator
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'create':
            return FoodgramUserCreateSerializer
        return FoodgramUserSerializer


class SubscriptionsViewSet(viewsets.ModelViewSet):
    """Класс-вьюсет для модели FoodgramUser."""
    http_method_names = ['get', 'post', 'delete']
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = FoodgramPaginator

    def get_queryset(self):
        user = self.request.user
        return Subscription.objects.filter(
            user=user
        ).prefetch_related('author')

    def delete(self, request, *args, **kwargs):
        author_id = kwargs.get("id", None)
        author = get_object_or_404(FoodgramUser, id=author_id)
        user = request.user
        get_object_or_404(Subscription, user_id=user.id,
                          author_id=author.id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
