from django.contrib import admin

from . import models


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('title', 'dimension')
    search_fields = ('title',)
    list_filter = ('title', )


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author')
    search_fields = ('title', 'author')
    list_filter = ('author__username', 'title', 'tag')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')


class VolumeIngredientAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'quantity', 'recipe')
    search_fields = ('ingredient',)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user',)


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user',)


admin.site.register(models.Purchase, PurchaseAdmin)
admin.site.register(models.Favorite, FavoriteAdmin)
admin.site.register(models.Subscription, SubscriptionAdmin)
admin.site.register(models.VolumeIngredient, VolumeIngredientAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.Tag, TagAdmin)
