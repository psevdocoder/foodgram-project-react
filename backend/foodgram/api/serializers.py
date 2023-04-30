from django.contrib.auth.password_validation import validate_password
from django.db import transaction
import djoser.serializers as djoser_serializers
from rest_framework import serializers
from django.core import exceptions as django_exceptions
from drf_base64.fields import Base64ImageField

from food.models import Recipe, Ingredient, Tag, IngredientAmount, Favorite, \
    ShoppingCart
from users.models import User, Subscribe


"""================================= users ================================="""


class UserReadSerializer(djoser_serializers.UserSerializer):
    """[GET] Список пользователей."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        """
        Возвращает флаг, указывающий, подписан ли текущий пользователь на
        указанного пользователя
        @param obj: объект пользователя
        @return: Флаг, указывающий, подписан ли текущий пользователь
        на указанного пользователя.
        """
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Subscribe.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()
        return False


class UserCreateSerializer(djoser_serializers.UserCreateSerializer):
    """[POST] Создание нового пользователя."""
    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'password')
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
        }

    def validate(self, obj):
        """
        Проверяет, что имя пользователя является допустимым и возвращает
        объект для создания пользователя
        @param obj: словарь с данными пользователя
        @return: возвращает словарь с проверенными данными пользователя
        """
        invalid_usernames = ['me', 'set_password',
                             'subscriptions', 'subscribe']
        if self.initial_data.get('username') in invalid_usernames:
            raise serializers.ValidationError(
                {'username': 'Вы не можете использовать это имя пользователя.'}
            )
        return obj


class SetPasswordSerializer(serializers.Serializer):
    """[POST] Изменение пароля пользователя."""
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, obj):
        """
        Проверяет валидность нового пароля пользователя
        @param obj: словарь, содержащий новый пароль и текущий пароль
        @return: валидные данные
        """
        try:
            validate_password(obj['new_password'])
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {'new_password': list(e.messages)}
            )
        return super().validate(obj)

    def update(self, instance, validated_data):
        """
        Обновляет пароль пользователя
        @param instance: экземпляр модели пользователя
        @param validated_data:Словарь, содержащий новый пароль и текущий пароль
        @return: обновленные данные.
        """
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'Неправильный пароль.'}
            )
        if (validated_data['current_password']
           == validated_data['new_password']):
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от текущего.'}
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


class RecipeSerializer(serializers.ModelSerializer):
    """Список рецептов."""
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
    """[GET] Список авторов на которых подписан пользователь."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        """
        Определяет, подписан ли текущий пользователь на автора
        @param obj: экземпляр модели User
        @return: True, если пользователь подписан, иначе False
        """
        return (
            self.context.get('request').user.is_authenticated
            and Subscribe.objects.filter(user=self.context['request'].user,
                                         author=obj).exists()
        )

    @staticmethod
    def get_recipes_count(obj):
        """
        Получает количество рецептов у автора
        @param obj: экземпляр модели User
        @return: количество рецептов у автора
        """
        return obj.recipes.count()

    def get_recipes(self, obj):
        """
        Получает список рецептов автора
        @param obj: экземпляр модели User
        @return: список рецептов автора
        """
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data


class SubscribeAuthorSerializer(serializers.ModelSerializer):
    """[POST, DELETE] Подписка на автора и отписка."""
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def validate(self, obj):
        """
        Проверка подписки на автора
        @param obj: экземпляр модели User
        @return: экземпляр модели User после проверки
        """
        if self.context['request'].user == obj:
            raise serializers.ValidationError({'errors': 'Ошибка подписки.'})
        return obj

    def get_is_subscribed(self, obj):
        """
        Определяет, подписан ли текущий пользователь на автора
        @param obj: экземпляр модели User
        @return: True, если пользователь подписан, иначе False
        """
        return (
            self.context.get('request').user.is_authenticated
            and Subscribe.objects.filter(user=self.context['request'].user,
                                         author=obj).exists()
        )

    @staticmethod
    def get_recipes_count(obj):
        """
        Получает количество рецептов у автора
        @param obj: экземпляр модели User
        @return: количество рецептов у автора
        """
        return obj.recipes.count()


"""================================= food =================================="""


class IngredientSerializer(serializers.ModelSerializer):
    """[GET] Список ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """[GET] Список тегов."""
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Список ингредиентов с количеством для рецепта."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name',
                  'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """[GET] Список рецептов."""
    author = UserReadSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source='recipes')
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags',
                  'author', 'ingredients',
                  'is_favorite', 'is_in_shopping_cart',
                  'name', 'image',
                  'text', 'cooking_time')

    def get_is_favorite(self, obj):
        """
        Определяет, добавлен ли рецепт в избранное у текущего пользователя
        @param obj: экземпляр модели Recipe
        @return: True, если рецепт добавлен в избранное, иначе False
        """

        return (
            self.context.get('request').user.is_authenticated
            and Favorite.objects.filter(user=self.context['request'].user,
                                        recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """
        Определяет, добавлен ли рецепт в список покупок у текущего пользователя
        @param obj: экземпляр модели Recipe
        @return: True, если рецепт добавлен в список покупок, иначе False
        """
        return (
                self.context.get('request').user.is_authenticated
                and ShoppingCart.objects.filter(
                user=self.context['request'].user,
                recipe=obj).exists()
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Ингредиент и количество для создания рецепта."""
    id = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """[POST, PATCH, DELETE] Создание, изменение и удаление рецепта."""
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    author = UserReadSerializer(read_only=True)
    id = serializers.ReadOnlyField()
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients',
                  'tags', 'image',
                  'name', 'text',
                  'cooking_time', 'author')
        extra_kwargs = {
            'ingredients': {'required': True, 'allow_blank': False},
            'tags': {'required': True, 'allow_blank': False},
            'name': {'required': True, 'allow_blank': False},
            'text': {'required': True, 'allow_blank': False},
            'image': {'required': True, 'allow_blank': False},
            'cooking_time': {'required': True},
        }

    def validate(self, obj):
        """
        Проверяет, что все обязательные поля заполнены и ингредиенты уникальны
        @param obj: объект для проверки
        @return: obj: проверенный объект
        """
        for field in ['name', 'text', 'cooking_time']:
            if not obj.get(field):
                raise serializers.ValidationError(
                    f'{field} - Обязательное поле.'
                )
        if not obj.get('tags'):
            raise serializers.ValidationError(
                'Нужно указать минимум 1 тег.'
            )
        if not obj.get('ingredients'):
            raise serializers.ValidationError(
                'Нужно указать минимум 1 ингредиент.'
            )
        ingredient_id_list = [item['id'] for item in obj.get('ingredients')]
        unique_ingredient_id_list = set(ingredient_id_list)
        if len(ingredient_id_list) != len(unique_ingredient_id_list):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальны.'
            )
        return obj

    @transaction.atomic
    def tags_and_ingredients_set(self, recipe, tags, ingredients):
        """
        Метод для сохранения тегов и ингредиентов рецепта
        @param recipe: объект модели Recipe
        @param tags: список объектов модели Tag
        @param ingredients: список объектов модели RecipeIngredient
        """

        recipe.tags.set(tags)
        IngredientAmount.objects.bulk_create(
            [IngredientAmount(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        """
        Создание нового рецепта
        @param validated_data: данные, полученные от пользователя
        @return: созданный рецепт
        """
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        self.tags_and_ingredients_set(recipe, tags, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Обновляет рецепт с заданными данными в экземпляре модели
        @param instance: экземпляр модели рецепта, который нужно обновить
        @param validated_data: словарь с данными для обновления рецепта
        @return: обновленный рецепта
        """
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        IngredientAmount.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()).delete()
        self.tags_and_ingredients_set(instance, tags, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Преобразование экземпляра модели в представление
        @param instance: экземпляр модели рецепта
        @return: данные рецепта в формате, определенном в RecipeReadSerializer
        """
        return RecipeReadSerializer(instance,
                                    context=self.context).data
