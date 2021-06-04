from recipes.models import Ingredient, VolumeIngredient
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from foodgram.settings import PAGINATOR_PAGES

User = get_user_model()


# рецепты с фильтрацией по тегам и аннотированием
def get_recipes_by_tags(request, recipes):
    active_tags = request.META['active_tags']
    if active_tags:
        recipes = recipes.get_by_tags(tags=active_tags)
    recipes = (recipes.is_annotated(user=request.user)
               if request.user.is_authenticated
               else recipes)
    return recipes


# разбиваю элементы на страницы
def split_on_page(request, objects_on_page):
    paginator = Paginator(objects_on_page, PAGINATOR_PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return {'page': page, 'paginator': paginator}


# проверка превышения страниц в запросе, генерация url и рендер/редирект
def check_paginator(request, selection, template, context):
    limit_page = selection['paginator'].num_pages
    page_number = request.GET.get('page')
    check = (page_number is not None and int(page_number) > limit_page)
    url_tail = ''
    for tag in request.META['active_tags']:
        url_tail = f'{url_tail}&filter={tag}'
    url_head = request.path
    url = f'{url_head}?page={limit_page}{url_tail}'
    if check:
        return redirect(url)
    return render(request, template, context)
