from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404, redirect, render


class AuthorView(TemplateView):
    template_name = 'service_pages/author.html'


class TechView(TemplateView):
    template_name = 'service_pages/tech.html'


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


def bad_request(request, exception):
    return render(request, 'misc/400.html', {'path': request.path}, status=400)