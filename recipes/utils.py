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


# def get_ingredients(request):
#     ingredients = {}
#     for key, title in request.POST.items():
#         if not key.startswith('nameIngredient_'):
#             continue
#         arg = key.split('_')[1]
#         amount = request.POST['valueIngredient_' + arg]
#         ingredients[title] = amount
#     return ingredients


def get_ingredients(ingredients, recipe):
    ingredients_for_save = []
    for ingredient in ingredients:
        product = get_object_or_404(Ingredient, title=ingredient['title'])
        ingredients_for_save.append(
            VolumeIngredient(
                recipe=recipe,
                ingredient=product,
                quantity=ingredient['quantity']
            )
        )
    return ingredients_for_save


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
