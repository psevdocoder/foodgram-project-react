# from django.contrib import admin
#
# from food import models
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
# @admin.register(models.Recipe)
# class RecipeAdmin(admin.ModelAdmin):
#     list_display = ('pk', 'name', 'author', 'in_favorites')
#     list_editable = (
#         'name', 'cooking_duration', 'text', 'tags',
#         'image', 'author'
#     )
#     readonly_fields = ('in_favorites',)
#     list_filter = ('name', 'author', 'tags')
#     empty_value_display = '-пусто-'
#
#     @admin.display(description='В избранном')
#     def in_favorites(self, obj):
#         return obj.favorite_recipe.count()
#
#
# @admin.register(models.Recipe_ingredient)
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
