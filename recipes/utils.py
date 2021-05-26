from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

from foodgram.settings import PAGINATOR_PAGES

User = get_user_model()


# рецепты с фильтрацией по тегам и аннотированием
def get_recipes_by_tags(request, recipes):
    active_tags = request.META['active_tags']
    if active_tags:
        recipes = recipes.filter(tag__value__in=active_tags).distinct()
    recipes = (recipes.is_annotated(user=request.user)
               if request.user.is_authenticated
               else recipes)
    context = {'recipes': recipes, 'filters': request.META['url_tail_tags']}
    return context


# разбиваю элементы на страницы
def split_on_page(request, objects_on_page):
    paginator = Paginator(objects_on_page, PAGINATOR_PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return {'page': page, 'paginator': paginator}


# проверка превышения страниц в запросе и генерация url
def page_out_of_paginator(request, selection):
    limit_page = selection['paginator'].num_pages
    page_number = request.GET.get('page')
    check = (page_number is not None and int(page_number) > limit_page)
    url_tail = ''
    for tag in request.META['active_tags']:
        url_tail = f'{url_tail}&filters={tag}'
    url_head = request.path
    url = f'{url_head}?page={limit_page}{url_tail}'
    return [check, url]
