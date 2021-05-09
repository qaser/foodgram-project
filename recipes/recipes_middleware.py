import re

from django.shortcuts import redirect

from .models import Tag


def all_tags(request):
    all_tags = Tag.objects.all()
    return all_tags


# можно этого не делать. для единообразия работы с тегами
def active_tags(request):
    return request.GET.getlist('filters')


# def insert_tags(request):
#     response = self.get_response(request)
#         print(response)
#         page = request.GET.get('page')


class TagsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.META['all_tags'] = all_tags(request)
        request.META['active_tags'] = active_tags(request)
        return self.get_response(request)


# class PaginatorMiddleware:
#     """Redirect to last_page if non valid paginator."""

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         response = self.get_response(request)
#         # print(request.context)
#         # print(dir(response))
#         page = request.GET.get('page')
#         # print(f'{page} page')
#         try:
#             paginator = response.get('paginator')
#             # print(f'{paginator} paginator')
#         except AttributeError:
#             paginator = None
#         # print(f'{paginator} paginator')
#         if (page and paginator) and (page.isdigit() is False or int(page) > paginator.num_pages):
#             filters = request.GET.get('filters')
#             print(filters)
#             full_path = f'{request.path}?page={paginator.num_pages}'
#             if filters:
#                 full_path = f'{full_path}&filters={filters}'
#                 print(full_path)
#             return redirect(full_path)
#         return response


