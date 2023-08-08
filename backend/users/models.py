from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from api.validators import model_validate_username


class FoodgramUser(AbstractUser):
    """Класс управления данными пользователей Foodgram."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    username = models.CharField(
        max_length=settings.MAX_LENGTH_USERNAME,
        verbose_name='Имя пользователя',
        help_text='Ваше имя на сайте',
        unique=True,
        null=False,
        blank=False,
        validators=[model_validate_username]
    )

    email = models.EmailField(
        max_length=settings.MAX_LENGTH_EMAIL,
        verbose_name='Электронная почта',
        unique=True,
        blank=False,
        null=False
    )
    first_name = models.CharField(
        max_length=settings.MAX_LENGTH_FIRST_NAME,
        verbose_name='Имя',
        help_text='Укажите имя пользователя',
        blank=True,
    )
    last_name = models.CharField(
        max_length=settings.MAX_LENGTH_LAST_NAME,
        verbose_name='Фамилия',
        help_text='Укажите фамилию пользователя',
        blank=True,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Класс управления данными подписок пользователей на авторов."""
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь'
    )

    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscribe',
        verbose_name='Автор'
    )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='no_self_subscription'
            )
        ]
        ordering = ('-id',)
