from django.contrib import admin

from . import models


class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author',
        'image', 'time',
        'slug', 'pub_date'
    )
    search_fields = ('tag', 'author')
    list_filter = ('pub_date', 'tag', 'author')
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measure')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'quantity')


admin.site.register(models.Recipe, RecipesAdmin)
admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.RecipeIngredient, RecipeIngredientAdmin)
