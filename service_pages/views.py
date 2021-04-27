from django.views.generic.base import TemplateView


class AuthorView(TemplateView):
    template_name = 'service_pages/author.html'


class TechView(TemplateView):
    template_name = 'service_pages/tech.html'
