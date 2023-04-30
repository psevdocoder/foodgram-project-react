# from django.contrib import admin
#
# from food import models
# from food.models import TagRecipe, IngredientAmount, Favorite
#
#
# @admin.register(models.Ingredient)
# class IngredientAdmin(admin.ModelAdmin):
#     list_display = ('pk', 'name', 'measurement_unit')
#     list_filter = ('name', )
#     search_fields = ('name', )
#
#
# @admin.register(models.Tag)
# class TagAdmin(admin.ModelAdmin):
#     list_display = ('pk', 'name', 'color', 'slug')
#     list_editable = ('name', 'color', 'slug')
#     empty_value_display = '-пусто-'
#
#
# class TagInline(admin.TabularInline):
#     """Вспомогательный класс для отображения тэгов в модели рецептов"""
#     model = TagRecipe
#     extra = 3
#
#
# class IngredientsInline(admin.TabularInline):
#     """Вспомогательный класс для отображения игредиентов в модели рецептов"""
#     model = IngredientAmount
#     extra = 3
#
#
# class RecipeAdmin(admin.ModelAdmin):
#     """Класс отображения в админке модели рецептов"""
#     inlines = (TagInline, IngredientsInline)
#     list_display = (
#         'id', 'name', 'author', 'cooking_time', 'image', 'pub_date'
#     )
#     list_display_links = ('id', 'name')
#     search_fields = ('name', 'author__username')
#     list_filter = ('tags', 'pub_date',)
#     readonly_fields = ('count_add_favorited',)
#     empty_value_display = '-пусто-'
#
#     def count_add_favorited(self, obj):
#         return Favorite.objects.filter(recipe=obj).count()
#
#     count_add_favorited.short_description = 'Сколько раз добавлен в избранное'
#
#
# @admin.register(models.IngredientAmount)
# class RecipeIngredientAdmin(admin.ModelAdmin):
#     list_display = ('pk', 'recipe', 'ingredient', 'amount')
#     list_editable = ('recipe', 'ingredient', 'amount')
#
#
# @admin.register(models.Favorite)
# class FavoriteAdmin(admin.ModelAdmin):
#     list_display = ('pk', 'user', 'recipe')
#     list_editable = ('user', 'recipe')
#
#
# @admin.register(models.Shopping_cart)
# class ShoppingCartAdmin(admin.ModelAdmin):
#     list_display = ('pk', 'user', 'recipe')
#     list_editable = ('user', 'recipe')

from django.contrib import admin

from food.models import TagRecipe, IngredientAmount, Favorite, Recipe, \
    ShoppingCart, Tag, Ingredient
from users.models import Subscribe


class TagInline(admin.TabularInline):
    """Вспомогательный класс для отображения тэгов в модели рецептов"""
    model = TagRecipe
    extra = 3


class IngredientsInline(admin.TabularInline):
    """Вспомогательный класс для отображения игредиентов в модели рецептов"""
    model = IngredientAmount
    extra = 3


class RecipeAdmin(admin.ModelAdmin):
    """Класс отображения в админке модели рецептов"""
    inlines = (TagInline, IngredientsInline)
    list_display = (
        'id', 'name', 'author', 'cooking_duration', 'image', 'pub_date'
    )
    list_display_links = ('id', 'name')
    search_fields = ('name', 'author__username')
    list_filter = ('tags', 'pub_date',)
    readonly_fields = ('count_add_favorited',)
    empty_value_display = '-пусто-'

    def count_add_favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    count_add_favorited.short_description = 'Сколько раз добавлен в избранное'


class IngredientAdmin(admin.ModelAdmin):
    """Класс отображения в админке модели ингедиентов"""
    list_display = ('id', 'name', 'measurement_unit')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    list_editable = ()


class IngredientAmountAdmin(admin.ModelAdmin):
    """Класс отображения в админке модели ингредиентов в рецептах"""
    list_display = ('id', 'ingredient', 'recipe', 'amount')
    list_display_links = ('id', 'ingredient')
    empty_value_display = '-пусто-'


class TagtAdmin(admin.ModelAdmin):
    """Класс отображения в админке модели тэгов"""
    list_display = ('id', 'name', 'slug', 'color')
    list_display_links = ('id', 'name')
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
# admin.site.register(Subscribe)
admin.site.register(Tag, TagtAdmin)
admin.site.register(TagRecipe)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
