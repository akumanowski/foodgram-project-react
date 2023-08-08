from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FoodgramUserViewSet, SubscriptionsViewSet,
                    RecipeViewSet, TagViewSet,
                    IngredientViewSet, FavoriteViewSet, ShoppingListViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('users', FoodgramUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('users/subscriptions/',
         SubscriptionsViewSet.as_view({'get': 'list'}),
         name='subscriptions'),
    path('users/<id>/subscribe/',
         SubscriptionsViewSet.as_view({'post': 'create', 'delete': 'delete'}),
         name='subscribe'),
    path('recipes/download_shopping_cart/',
         ShoppingListViewSet.as_view({'get': 'download_shopping_cart'}),
         name='download_shopping_cart'),
    path('recipes/<id>/shopping_cart/',
         ShoppingListViewSet.as_view({'post': 'create', 'delete': 'delete'}),
         name='cart'),
    path('recipes/<id>/favorite/',
         FavoriteViewSet.as_view({'post': 'create', 'delete': 'delete'}),
         name='favorite'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
