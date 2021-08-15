from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from foodgram.settings import PAGINATOR_PAGES

User = get_user_model()


# разбиваю элементы на страницы
def split_on_page(request, objects_on_page):
    paginator = Paginator(objects_on_page, PAGINATOR_PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return {'page': page}


# проверка превышения страниц в запросе, генерация url и рендер/редирект
def check_paginator(request, selection, template, context):
    limit_page = selection['page'].paginator.num_pages
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
