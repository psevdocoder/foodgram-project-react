from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify
from unidecode import unidecode

from users.models import User


class Tag(models.Model):
    name = models.CharField(verbose_name='Тэг', max_length=200, unique=True)
    color = ColorField(verbose_name='Цвет')
    slug = models.SlugField(
        verbose_name='Уникальный slug', unique=True, null=True, max_length=200
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название', max_length=200)
    measurement_unit = models.CharField(verbose_name='Единица измерения',
                                        max_length=20)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        unique_together = ('name', 'measurement_unit')

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название', max_length=200, unique=True)
    text = models.TextField('Описание')
    author = models.ForeignKey(to=User, on_delete=models.CASCADE,
                               related_name='recipes', verbose_name='Автор')
    image = models.ImageField(verbose_name='Картинка',
                              upload_to='recipes/', blank=True)
    ingredients = models.ManyToManyField(
        to=Ingredient, through='IngredientAmount',
        through_fields=('recipe', 'ingredient'), verbose_name='Ингредиенты')
    tags = models.ManyToManyField(
        to=Tag, verbose_name='Тэги', through='TagRecipe')
    pub_date = models.DateTimeField(
        verbose_name='Время публикации', auto_now_add=True)
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinValueValidator(1)])

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    """Кастомная модель связи тегов и рецепта"""
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name='Наименование'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tags_ref',
        verbose_name='Рецепт'
    )

    def __str__(self):
        return f'{self.recipe}<-->{self.tag}'

    class Meta:
        verbose_name = 'Тэг в рецепте'
        verbose_name_plural = 'Тэги в рецепте'


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipes', verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredients',
                                   verbose_name='Ингредиент')
    amount = models.IntegerField('Количество',
                                 validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                               name='unique_combination')]

    def __str__(self):
        return (f'{self.recipe.name}: {self.ingredient.name} - '
                f'{self.amount} {self.ingredient.measurement_unit}')


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorite_user',
                             verbose_name='Добавил в избранное')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favorite_recipe',
                               verbose_name='Избранный рецепт')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                                               name='unique_favorite')]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='shopping_user',
                             verbose_name='Добавил в корзину')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='shopping_recipe',
                               verbose_name='Рецепт в корзине')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                                               name='unique_shopping_cart')]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
