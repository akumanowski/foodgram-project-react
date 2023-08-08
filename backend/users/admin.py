from django.contrib.admin import ModelAdmin, register
from django.contrib.auth.admin import UserAdmin

from . import models


@register(models.FoodgramUser)
class FoodgramUserAdmin(UserAdmin):
    """Класс управления отображением данных пользователя Foodgram."""
    list_display = ('id', 'username', 'email', 'password', 'first_name',
                    'last_name')
    list_display_links = ('id', 'username')
    list_filter = ('username', 'email')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    empty_value_display = '-пусто-'


@register(models.Subscription)
class SubscribeAdmin(ModelAdmin):
    """Класс управления отображением данных подписчиков Foodgram."""
    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')
    list_display_links = ('id', 'user')
    empty_value_display = '-пусто-'
