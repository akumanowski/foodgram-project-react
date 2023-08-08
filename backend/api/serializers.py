"""Модуль сериалайзер приложения Api."""
import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import (UserCreateSerializer, UserSerializer)
from rest_framework.serializers import (ModelSerializer, ImageField,
                                        ReadOnlyField, IntegerField,
                                        SerializerMethodField,
                                        PrimaryKeyRelatedField,
                                        ValidationError)
from recipes.models import (Tag, Ingredient, Recipe, IngredientInRecipe,
                            Favorite, ShoppingList)
from users.models import Subscription, FoodgramUser

User = get_user_model()


class Base64ImageField(ImageField):
    """Класс для работы с изображениями в кодировке Base64"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(ModelSerializer):
    """Cериализатор тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    """Cериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(ModelSerializer):
    """Сериализатор списка ингредиентов с количеством для рецепта."""
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id',
                  'name',
                  'measurement_unit',
                  'amount')


class IngredientInRecipeCreateSerializer(ModelSerializer):
    """Сериализатор создания списка ингредиентов с количеством для рецепта."""
    id = IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id',
                  'amount')


class FoodgramUserSerializer(UserSerializer):
    """Cериализатор пользователей Foodgram."""
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        requests = self.context.get('request')
        if requests is None:
            return False
        return (requests.user.is_authenticated
                and Subscription.objects.filter(
                    user__id=self.context['request'].user.id,
                    author__id=obj.id
                ).exists())


class FoodgramUserCreateSerializer(UserCreateSerializer):
    """Cериализатор для создания пользователей Foodgram."""

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password')


class SimpleRecipeSerializer(ModelSerializer):
    """Упрощенный сериализатор рецептов."""

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time')


class RecipeReadSerializer(ModelSerializer):
    """Cериализатор чтения рецептов."""
    author = FoodgramUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = SerializerMethodField(
        method_name='get_ingredients'
    )
    is_favorited = SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    def get_ingredients(self, obj):
        ingredients = IngredientInRecipe.objects.filter(recipe=obj)
        serializer = IngredientInRecipeSerializer(ingredients, many=True)
        return serializer.data

    def get_is_favorited(self, obj):
        requests = self.context.get('request')
        if requests is None:
            return False
        return (requests.user.is_authenticated
                and Favorite.objects.filter(user=self.context['request'].user,
                                            recipe=obj).exists()
                )

    def get_is_in_shopping_cart(self, obj):
        requests = self.context.get('request')
        if requests is None:
            return False
        user = requests.user
        if user.is_anonymous:
            return False
        return ShoppingList.objects.filter(user=user, recipe=obj).exists()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')


class RecipeChangeSerializer(ModelSerializer):
    """Сериализатор создания, изменения и удаления рецептов."""
    tags = PrimaryKeyRelatedField(many=True,
                                  queryset=Tag.objects.all())
    author = FoodgramUserSerializer(read_only=True)
    id = ReadOnlyField()
    ingredients = IngredientInRecipeCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'name',
                  'image',
                  'text',
                  'cooking_time')
        extra_kwargs = {
            'ingredients': {'required': True, 'allow_blank': False},
            'tags': {'required': True, 'allow_blank': False},
            'name': {'required': True, 'allow_blank': False},
            'text': {'required': True, 'allow_blank': False},
            'image': {'required': True, 'allow_blank': False},
            'cooking_time': {'required': True},
        }

    def validate(self, obj):
        if not obj.get('tags'):
            raise ValidationError(
                'Нужно указать минимум 1 тег.'
            )
        if not obj.get('ingredients'):
            raise ValidationError(
                'Нужно указать минимум 1 ингредиент.'
            )
        inrgedient_id_list = [item['id'] for item in obj.get('ingredients')]
        unique_ingredient_id_list = set(inrgedient_id_list)
        if len(inrgedient_id_list) != len(unique_ingredient_id_list):
            raise ValidationError(
                'Ингредиенты должны быть уникальны.'
            )
        return obj

    @transaction.atomic
    def tags_and_ingredients_set(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, pk=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        self.tags_and_ingredients_set(recipe, tags, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        super().update(instance, validated_data)
        IngredientInRecipe.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()).delete()
        self.tags_and_ingredients_set(instance, tags, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance,
                                    context=self.context).data


class RecipesDataWorkerSerializer(ModelSerializer):
    """Шаблон сериализатора для моделей, ссылающихся на рецепты."""
    ERROR_MSG = "На этот рецепт уже есть ссылка"

    def validate(self, data):
        request = self.context.get('request', None)
        recipe_id = request.parser_context.get(
            'kwargs').get('id')
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if self.Meta.model.objects.filter(user=user,
                                          recipe=recipe).exists():
            raise ValidationError({'errors': self.ERROR_MSG})
        data = {'recipe': recipe, 'user': user}
        return data


class FavoriteSerializer(RecipesDataWorkerSerializer):
    """Сериализатор для добавления и удаления рецептов в списке избранного."""
    ERROR_MSG = "Рецепт уже в избранном"

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)
        read_only_fields = ('user', 'recipe',)

    def to_representation(self, instance):
        request = self.context.get('request')
        return SimpleRecipeSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class ShoppingListSerializer(RecipesDataWorkerSerializer):
    """Сериалайзер для добавления и удаления рецептов в списке покупок."""
    ERROR_MSG = "Рецепт уже в списке покупок"

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe',)
        read_only_fields = ('user', 'recipe',)

    def to_representation(self, instance):
        request = self.context.get('request')
        return SimpleRecipeSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class SubscriptionSerializer(ModelSerializer):
    """Cериализатор подписчиков Foodgram."""
    email = ReadOnlyField(source='author.email')
    id = ReadOnlyField(source='author.id')
    username = ReadOnlyField(source='author.username')
    first_name = ReadOnlyField(source='author.first_name')
    last_name = ReadOnlyField(source='author.last_name')
    is_subscribed = SerializerMethodField(read_only=True)
    recipes = SerializerMethodField(read_only=True)
    recipes_count = SerializerMethodField(read_only=True)

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        condition_1 = self.context.get('request').user.is_authenticated
        condition_2 = Subscription.objects.filter(user=user,
                                                  author=obj.author).exists()
        return condition_1 and condition_2

    def validate(self, data):
        request = self.context.get('request', None)
        author_id = request.parser_context.get(
            'kwargs').get('id')
        user = request.user
        author = get_object_or_404(FoodgramUser, id=author_id)

        if Subscription.objects.filter(user=user, author_id=author).exists():
            raise ValidationError(
                {'errors': f'Внимание! Вы уже подписаны на {author}'}
            )
        if user == author:
            raise ValidationError(
                {'errors': 'По правилам Foodgram подписка на '
                           'самого себя запрещена!'}
            )
        data = {'author': author, 'user': user}
        return data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        query_params = request.query_params
        queryset = Recipe.objects.filter(author=obj.author)
        if 'recipes_limit' in query_params:
            recipes_limit = query_params['recipes_limit']
            queryset = queryset[:int(recipes_limit)]
        serializer = SimpleRecipeSerializer(queryset, many=True)
        return serializer.data
