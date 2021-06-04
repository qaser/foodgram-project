from .models import Tag


def url_tail_tags(request):
    url_tail = ''
    for tag in request.META['active_tags']:
        url_tail = '{}{}'.format(url_tail, f'&filter={tag}')
    return url_tail


class TagsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.all_tags = [{'attrs': attr} for attr in Tag.objects.all()]

    def __call__(self, request):
        # для реализации "новой" системы тегов использую
        # два вида ссылок: первичная и обычная
        # первичная генерируется при первой загрузке страницы,
        # когда все теги активны, затем генерируется обычная ссылка
        # соответственно в шаблоне tags.html есть условие if
        active_tags = request.GET.getlist('filter')
        count_active_tags = len(active_tags)
        all_filters = [_tag['attrs'].value for _tag in self.all_tags]
        for tag in self.all_tags:
            filters = active_tags.copy()
            primal_filters = all_filters.copy()
            if tag['attrs'].value in active_tags and count_active_tags > 1:
                tag['active'] = True
                filters.remove(tag['attrs'].value)
            elif tag['attrs'].value in active_tags and count_active_tags == 1:
                tag['active'] = True
            else:
                tag['active'] = False
                filters.append(tag['attrs'].value)
            url_end = '&filter='.join(filters)
            primal_filters.remove(tag['attrs'].value)
            primal_url_end = '&filter='.join(primal_filters)
            tag['url'] = f'?filter={url_end}'  # обычный урл
            tag['primal_url'] = f'?filter={primal_url_end}'  # первичный урл
        request.META['active_tags'] = active_tags
        request.META['url_tail_tags'] = url_tail_tags(request)
        request.META['all_tags'] = self.all_tags
        request.META['count_active_tags'] = count_active_tags
        return self.get_response(request)
