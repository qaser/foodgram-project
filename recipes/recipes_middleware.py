from .models import Tag


def all_tags(request):
    all_tags = Tag.objects.all()
    return all_tags


# можно этого не делать. для единообразия работы с тегами
def active_tags(request):
    return request.GET.getlist('filters')


class TagsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.META['all_tags'] = all_tags(request)
        request.META['active_tags'] = active_tags(request)
        return self.get_response(request)
