import json
from django.http import JsonResponse
from django.views.generic import View
from django.shortcuts import get_object_or_404

from recipes.models import (
    User, Ingredient, Recipe, Favorite, Subscription, Purchase
)


class Ingredients(View):
    def get(self, request):
        text = request.GET.get('query')
        ingredients = list(
            Ingredient.objects.filter(title__icontains=text).values(
                'title', 'dimension'
            )
        )
        return JsonResponse(ingredients, safe=False)


class Favorites(View):
    def post(self, request):
        recipe_id = json.loads(request.body).get('id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        Favorite.objects.get_or_create(user=request.user, recipe=recipe)
        return JsonResponse({'success': True})

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = get_object_or_404(User, username=request.user.username)
        obj = get_object_or_404(Favorite, user=user, recipe=recipe)
        obj.delete()
        return JsonResponse({'success': True})


class Purchases(View):
    def post(self, request):
        recipe_id = json.loads(request.body).get('id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        Purchase.objects.get_or_create(user=request.user, recipe=recipe)
        return JsonResponse({'success': True})

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = get_object_or_404(User, username=request.user.username)
        obj = get_object_or_404(Purchase, user=user, recipe=recipe)
        obj.delete()
        return JsonResponse({'success': True})


class Subscriptions(View):
    def post(self, request):
        author_id = json.loads(request.body).get('id')
        author = get_object_or_404(User, id=author_id)
        Subscription.objects.get_or_create(user=request.user, author=author)
        return JsonResponse({'success': True})

    def delete(self, request, author_id):
        user = get_object_or_404(User, username=request.user.username)
        author = get_object_or_404(User, id=author_id)
        obj = get_object_or_404(Subscription, user=user, author=author)
        obj.delete()
        return JsonResponse({'success': True})
