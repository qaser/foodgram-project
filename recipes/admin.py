from django.contrib import admin

from . import models


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('title', 'dimension')
    search_fields = ('title',)
    list_filter = ('title', )


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_author')
    search_fields = ('title', 'get_author')
    list_filter = ('author__username', 'title', 'tag')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')

    def get_author(self, obj):
        return obj.author.username


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'value')
    empty_value_display = 'None'


class VolumeIngredientAdmin(admin.ModelAdmin):
    list_display = ('get_ingredient', 'quantity', 'recipe')
    search_fields = ('get_ingredient',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ingredient')

    def get_units(self, obj):
        return obj.ingredient.dimension

    def get_ingredient(self, obj):
        return obj.ingredient.title


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'get_author')
    search_fields = ('get_user',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'author')

    def get_user(self, obj):
        return obj.user.username

    def get_author(self, obj):
        return obj.author.username


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'get_recipe')
    search_fields = ('get_user',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'recipe')

    def get_user(self, obj):
        return obj.user.username

    def get_recipe(self, obj):
        return obj.recipe.name


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'get_recipe')
    search_fields = ('get_user',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'recipe')

    def get_user(self, obj):
        return obj.user.username

    def get_recipe(self, obj):
        return obj.recipe.name


admin.site.register(models.Purchase, PurchaseAdmin)
admin.site.register(models.Favorite, FavoriteAdmin)
admin.site.register(models.Subscription, SubscriptionAdmin)
admin.site.register(models.VolumeIngredient, VolumeIngredientAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.Ingredient, IngredientAdmin)