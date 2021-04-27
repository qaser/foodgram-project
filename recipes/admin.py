from django.contrib import admin

from . import models


class IngredientQuantityInline(admin.TabularInline):
    model = models.Recipe.ingredients.through
    min_num = 1


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('title', 'dimension')
    search_fields = ('title',)
    list_filter = ('dimension', )


class RecipeAdmin(admin.ModelAdmin):
    def count_favorite(self,  obj):
        count = models.Favorite.favorites.filter(recipe=obj).count()
        return count

    list_display = ('title', 'author', 'time', 'count_favorite')
    search_fields = ('title', 'author', 'pub_date')
    list_filter = ('author__username', 'tag')
    readonly_fields = ('count_favorite',)
    inlines = (IngredientQuantityInline,)
    count_favorite.short_description = 'количество добавлений в избранное'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'color')
    list_filter = ('color',)

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
