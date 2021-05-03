import re

from django.shortcuts import redirect

from .models import Tag


def all_tags(request):
    all_tags = Tag.objects.all()
    return all_tags


def active_tags(request):
    return request.GET.getlist('filters')


class TagsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.META['all_tags'] = all_tags(request)
        request.META['active_tags'] = active_tags(request)
        return self.get_response(request)


class PaginatorMiddleware:
    """Redirect to last_page if non valid paginator."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        page = request.GET.get('page')
        try:
            paginator = response.context_data.get('paginator')
        except AttributeError:
            paginator = None
        if (page and paginator) and (page.isdigit() is False or int(page) > paginator.num_pages):
            q = request.GET.get('q')
            full_path = f'{request.path}?page={paginator.num_pages}'
            if q:
                full_path = f'{full_path}&q={q}'
            return redirect(full_path)
        return response
