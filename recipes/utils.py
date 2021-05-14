from foodgram.settings import PAGINATOR_PAGES
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from .models import Ingredient, Tag, VolumeIngredient
from django.urls import reverse

User = get_user_model()


# рецепты с фильтрацией по тегам и аннотированием
def get_recipes_by_tags(request, recipes):
    filters = ''
    active_tags = request.META['active_tags']
    for tag in active_tags:
        filters += f'&filters={tag}'
    if active_tags:
        recipes = recipes.filter(tag__value__in=active_tags).distinct()
    recipes = recipes.is_annotated(user=request.user.is_authenticated)
    context = {'recipes': recipes, 'filters': filters}
    return context


# словарь ингредиентов для рецепта
def get_ingredients(request):
    ingredients = {}
    for key, ingredient_name in request.POST.items():
        if 'nameIngredient' in key:
            _ = key.split('_')
            ingredients[ingredient_name] = int(
                request.POST[f'valueIngredient_{_[1]}']
            )
    return ingredients


# разбиваю элементы на страницы
def split_on_page(request, objects_on_page):
    paginator = Paginator(objects_on_page, PAGINATOR_PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return {'page': page, 'paginator': paginator}


# проверка превышения страниц в запросе
def page_out_of_paginator(request, limit_page):
    page_number = request.GET.get('page')
    if page_number is not None and int(page_number) > limit_page:
        return True
    return False


# генерация строки запроса с тегами и последней страницей
def generate_path(request, limit_page):
    url_tail = ''
    for tag in request.META['active_tags']:
        url_tail = f'{url_tail}&filters={tag}'
    url = reverse(request.resolver_match.url_name)
    return f'{url}?page={limit_page}{url_tail}'


def save_recipe(recipe, ingredients, request):
    recipe.author = request.user
    recipe.save()
    recipe_ingredients = []

    for item in ingredients:
        recipe_ing = VolumeIngredient(
            quantity=item.get('quantity'),
            ingredient=Ingredient.objects.get(title=item.get('title')),
            recipe=recipe)
        recipe_ing.save()